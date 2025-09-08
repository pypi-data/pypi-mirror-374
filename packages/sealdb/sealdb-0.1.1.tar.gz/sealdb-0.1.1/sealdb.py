import json
import os
import re
from typing import List, Dict, Any, Union

class NestedResult:
    def __init__(self, data):
        self._data = data
        for key, record in data.items():
            record_obj = Record(record)
            setattr(self, f"_{key}", record_obj)
        
        if data:
            first_key = list(data.keys())[0]
            self.id = getattr(self, f"_{first_key}")
    
    def __str__(self):
        if not self._data:
            return "No results found"
        
        result_lines = []
        for key in self._data.keys():
            record_obj = getattr(self, f"_{key}")
            result_lines.append(f"ID: {key}")
            for field, value in record_obj.__dict__.items():
                if not field.startswith('_'):
                    result_lines.append(f"  {field}: {value}")
            result_lines.append("")
        
        return "\n".join(result_lines).strip()
    
    def __getattr__(self, name):
        if name.isdigit() and f"_{name}" in self.__dict__:
            return getattr(self, f"_{name}")
        elif name == "all":
            return [getattr(self, f"_{key}") for key in self._data.keys()]
        elif name == "first":
            if self._data:
                first_key = list(self._data.keys())[0]
                return getattr(self, f"_{first_key}")
            return None
        elif name == "last":
            if self._data:
                last_key = list(self._data.keys())[-1]
                return getattr(self, f"_{last_key}")
            return None
        raise AttributeError(f"No record found with ID '{name}'")
    
    def __getitem__(self, key):
        if isinstance(key, int):
            key = str(key)
        if key in self._data:
            return getattr(self, f"_{key}")
        raise KeyError(f"No record found with ID '{key}'")
    
    def __iter__(self):
        for key in self._data.keys():
            yield getattr(self, f"_{key}")
    
    def __len__(self):
        return len(self._data)

class Record:
    def __init__(self, data):
        for key, value in data.items():
            setattr(self, key, value)
    
    def __str__(self):
        result = []
        for attr, value in self.__dict__.items():
            if not attr.startswith('_'):
                result.append(f"{attr}: {value}")
        return "\n".join(result)

class sealdb:
    def __init__(self, filename="minidb.edb"):
        if not filename.endswith(".edb"):
            filename += ".edb"
        self.filename = filename

        if not os.path.exists(filename):
            with open(filename, "w", encoding="utf-8") as f:
                json.dump({}, f)

        self._load()
        self._update_last_ids()

    def _load(self):
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = {}

    def _save(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def _update_last_ids(self):
        self.last_ids = {}
        for table, rows in self.data.items():
            if rows:
                keys = [int(k) for k in rows.keys()]
                self.last_ids[table] = max(keys)
            else:
                self.last_ids[table] = 0

    def execute(self, command: str):
        if not command.strip():
            return "Empty command"
            
        cmd = command.strip().split()[0].upper()

        if cmd == "CREATE":
            parts = command.split()
            if len(parts) == 3 and parts[1].upper() == "TABLE":
                table = parts[2]
                if table in self.data:
                    return f"Table '{table}' already exists"
                self.data[table] = {}
                self.last_ids[table] = 0
                self._save()
                return f"Table '{table}' created"
            return "Invalid CREATE syntax. Use: CREATE TABLE table_name"

        fields = self._parse_fields(command)
        table = fields.get("table")
        if not table:
            return "Table not specified"
        if table not in self.data:
            return f"Table '{table}' not found"

        if cmd == "INSERT":
            self.last_ids[table] += 1
            key = str(self.last_ids[table])
            record = {k: v for k, v in fields.items() if k != "table"}
            self.data[table][key] = record
            self._save()
            return f"Inserted into {table} with ID={key}"

        elif cmd == "GET":
            key = str(fields.get("key", ""))
            if not key:
                return "Key not specified"
            result = self.data[table].get(key)
            if result is None:
                return f"Record with ID={key} not found in table '{table}'"
            return NestedResult({key: result})

        elif cmd == "UPDATE":
            key = str(fields.pop("key", ""))
            if not key:
                return "Key not specified"
            if key in self.data[table]:
                self.data[table][key].update({k: v for k, v in fields.items() if k != "table"})
                self._save()
                return f"Updated record ID={key} in table '{table}'"
            return f"Record with ID={key} not found in table '{table}'"

        elif cmd == "DELETE":
            key = str(fields.get("key", ""))
            if not key:
                return "Key not specified"
            if key in self.data[table]:
                del self.data[table][key]
                self._save()
                return f"Deleted record ID={key} from table '{table}'"
            return f"Record with ID={key} not found in table '{table}'"

        elif cmd == "ALL":
            if not self.data[table]:
                return NestedResult({})
            return NestedResult(self.data[table])

        elif cmd == "QUERY":
            result = self._execute_query(table, fields)
            return NestedResult(result)

        return f"Unknown command: {cmd}"

    def _execute_query(self, table: str, fields: Dict[str, str]) -> Dict:
        conditions = {}
        order_by = None
        order_direction = "ASC"
        limit = None
        requested_fields = fields.get("fields")
        
        for key, value in fields.items():
            if key == "table" or key == "fields":
                continue
            elif key == "order":
                order_parts = value.split()
                if order_parts:
                    order_by = order_parts[0]
                    if len(order_parts) > 1 and order_parts[1].upper() in ["ASC", "DESC"]:
                        order_direction = order_parts[1].upper()
            elif key == "limit":
                try:
                    limit = int(value)
                except ValueError:
                    pass
            else:
                condition = self._parse_condition(key, value)
                if condition:
                    field_name = condition.get("field", key)
                    conditions[field_name] = condition

        results = {}
        for k, record in self.data[table].items():
            if self._matches_conditions(record, conditions):
                if requested_fields:
                    wanted = [f.strip() for f in requested_fields.split(",")]
                    filtered_record = {}
                    for f in wanted:
                        if f in record:
                            filtered_record[f] = record[f]
                    results[k] = filtered_record
                else:
                    results[k] = record

        if order_by and results:
            results = self._order_results(results, order_by, order_direction)

        if limit is not None and results:
            limited_results = {}
            for i, (k, v) in enumerate(results.items()):
                if i >= limit:
                    break
                limited_results[k] = v
            results = limited_results

        return results

    def _parse_condition(self, field: str, value: str) -> Dict[str, Any]:
        # الگوی regex برای شناسایی عملگرها
        operator_pattern = r'([a-zA-Z_][a-zA-Z0-9_]*)\s*([><]=?|!=|=|BETWEEN)\s*(.+)'
        match = re.match(operator_pattern, field)
        
        if not match:
            # اگر عملگر پیدا نشد، شرط ساده است (فیلد=مقدار)
            return {"operator": "=", "value": value, "field": field}
        
        field_name, operator, condition_value = match.groups()
        
        if operator.upper() == "BETWEEN":
            between_values = re.split(r'\s+AND\s+', condition_value, flags=re.IGNORECASE)
            if len(between_values) == 2:
                return {
                    "field": field_name,
                    "operator": "BETWEEN",
                    "values": [v.strip() for v in between_values]
                }
        
        return {
            "field": field_name,
            "operator": operator,
            "value": condition_value.strip()
        }

    def _matches_conditions(self, record: Dict, conditions: Dict) -> bool:
        for field_name, condition in conditions.items():
            if not self._check_condition(record, field_name, condition):
                return False
        return True

    def _check_condition(self, record: Dict, field_name: str, condition: Dict) -> bool:
        operator = condition["operator"]
        value = condition.get("value")
        values = condition.get("values", [])
        
        record_value = record.get(field_name)
        if record_value is None:
            return False
        
        # تبدیل مقادیر عددی در صورت امکان
        def try_convert(val):
            if isinstance(val, str):
                try:
                    if '.' in val:
                        return float(val)
                    else:
                        return int(val)
                except ValueError:
                    return val
            return val
        
        record_value = try_convert(record_value)
        value = try_convert(value) if value is not None else value
        values = [try_convert(v) for v in values] if values else []
        
        if operator == "=":
            return record_value == value
        elif operator == "!=":
            return record_value != value
        elif operator == ">":
            try:
                return record_value > value
            except TypeError:
                return str(record_value) > str(value)
        elif operator == "<":
            try:
                return record_value < value
            except TypeError:
                return str(record_value) < str(value)
        elif operator == ">=":
            try:
                return record_value >= value
            except TypeError:
                return str(record_value) >= str(value)
        elif operator == "<=":
            try:
                return record_value <= value
            except TypeError:
                return str(record_value) <= str(value)
        elif operator.upper() == "BETWEEN":
            try:
                return values[0] <= record_value <= values[1]
            except TypeError:
                return str(values[0]) <= str(record_value) <= str(values[1])
        
        return False

    def _order_results(self, results: Dict, order_by: str, direction: str = "ASC") -> Dict:
        def get_sort_key(item):
            key, record = item
            value = record.get(order_by)
            # سعی کن به عدد تبدیل کن، اگر ممکن نبود به عنوان رشته استفاده کن
            try:
                if isinstance(value, str):
                    if '.' in value:
                        return float(value)
                    else:
                        return int(value)
            except (ValueError, TypeError):
                pass
            return value
        
        try:
            sorted_items = sorted(results.items(), key=get_sort_key, 
                                 reverse=(direction.upper() == "DESC"))
            return dict(sorted_items)
        except TypeError:
            # اگر مرتب سازی با خطا مواجه شد، بدون مرتب سازی برگرد
            return results

    def _parse_fields(self, text: str):
        result = {}
        # جدا کردن دستور از پارامترها
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            return result
            
        # پارامترها را جدا کن
        params_text = parts[1].strip()
        if not params_text:
            return result
            
        # استفاده از regex برای جدا کردن پارامترها
        pattern = r'(\w+)=("[^"]*"|[^,]+)'
        matches = re.findall(pattern, params_text)
        
        for key, value in matches:
            value = value.strip()
            # حذف کوتیشن از مقادیر
            if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            result[key] = value
            
        return result