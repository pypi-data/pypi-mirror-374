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
        with open(self.filename, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def _save(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def _update_last_ids(self):
        self.last_ids = {}
        for table, rows in self.data.items():
            keys = [int(k) for k in rows.keys()] if rows else [0]
            self.last_ids[table] = max(keys)

    def execute(self, command: str):
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
            return "Invalid CREATE syntax"

        fields = self._parse_fields(command[len(cmd):])
        table = fields.get("table")
        if not table or table not in self.data:
            return "Table not found"

        if cmd == "INSERT":
            self.last_ids[table] += 1
            key = str(self.last_ids[table])
            record = {k: v for k, v in fields.items() if k != "table"}
            self.data[table][key] = record
            self._save()
            return f"Inserted into {table} with ID={key}"

        elif cmd == "GET":
            key = str(fields.get("key"))
            result = self.data[table].get(key)
            if result is None:
                return f"Record with ID={key} not found in table '{table}'"
            return NestedResult({key: result})

        elif cmd == "UPDATE":
            key = str(fields.pop("key", None))
            if key in self.data[table]:
                self.data[table][key].update({k: v for k, v in fields.items() if k != "table"})
                self._save()
                return f"Updated record ID={key} in table '{table}'"
            return f"Record with ID={key} not found in table '{table}'"

        elif cmd == "DELETE":
            key = str(fields.get("key"))
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

        return "Unknown command"

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
                order_by = order_parts[0]
                if len(order_parts) > 1 and order_parts[1].upper() in ["ASC", "DESC"]:
                    order_direction = order_parts[1].upper()
            elif key == "limit":
                try:
                    limit = int(value)
                except ValueError:
                    return {}
            else:
                condition = self._parse_condition(key, value)
                if condition:
                    conditions[key] = condition

        results = {}
        for k, record in self.data[table].items():
            if self._matches_conditions(record, conditions):
                if requested_fields:
                    wanted = [f.strip() for f in requested_fields.split(",")]
                    results[k] = {f: record.get(f) for f in wanted if f in record}
                else:
                    results[k] = record

        if order_by and results:
            results = self._order_results(results, order_by, order_direction)

        if limit and results:
            limited_results = {}
            for i, (k, v) in enumerate(results.items()):
                if i >= limit:
                    break
                limited_results[k] = v
            results = limited_results

        return results

    def _parse_condition(self, field: str, value: str) -> Dict[str, Any]:
        operator_pattern = r'([a-zA-Z_]+)\s*([><=!]+|BETWEEN)\s*(.+)'
        match = re.match(operator_pattern, field)
        
        if not match:
            return {"operator": "=", "value": value}
        
        field_name, operator, condition_value = match.groups()
        
        if operator.upper() == "BETWEEN":
            between_values = condition_value.split(" AND ")
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
        for field, condition in conditions.items():
            if not self._check_condition(record, condition):
                return False
        return True

    def _check_condition(self, record: Dict, condition: Dict) -> bool:
        if "field" in condition:
            field_name = condition["field"]
            operator = condition["operator"]
            value = condition.get("value")
            values = condition.get("values", [])
            
            record_value = record.get(field_name)
            if record_value is None:
                return False
                
            try:
                if isinstance(record_value, str) and record_value.replace('.', '', 1).isdigit():
                    record_value = float(record_value)
                if isinstance(value, str) and value.replace('.', '', 1).isdigit():
                    value = float(value)
                if values:
                    values = [float(v) if isinstance(v, str) and v.replace('.', '', 1).isdigit() else v for v in values]
            except ValueError:
                pass
            
            if operator == "=":
                return str(record_value) == str(value)
            elif operator == "!=":
                return str(record_value) != str(value)
            elif operator == ">":
                return record_value > value
            elif operator == "<":
                return record_value < value
            elif operator == ">=":
                return record_value >= value
            elif operator == "<=":
                return record_value <= value
            elif operator.upper() == "BETWEEN":
                return values[0] <= record_value <= values[1]
        else:
            return str(record.get(field_name)) == str(condition["value"])
        
        return False

    def _order_results(self, results: Dict, order_by: str, direction: str = "ASC") -> Dict:
        def get_sort_key(item):
            key, record = item
            value = record.get(order_by)
            try:
                if isinstance(value, str):
                    return float(value) if value.replace('.', '', 1).isdigit() else value
                return value
            except ValueError:
                return value
        
        sorted_items = sorted(results.items(), key=get_sort_key, 
                             reverse=(direction.upper() == "DESC"))
        return dict(sorted_items)

    def _parse_fields(self, text: str):
        result = {}
        items = re.split(r',(?=(?:[^"]*"[^"]*")*[^"]*$)', text)
        
        for item in items:
            item = item.strip()
            if "=" in item:
                k, v = item.split("=", 1)
                k = k.strip()
                v = v.strip()
                if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                    v = v[1:-1]
                result[k] = v
        return result