#!/usr/bin/python3

import csv
import json
import sys
from pathlib import Path
import re


def to_numeric(value):
    if not value:
        return value
    if value == "0":
        return 0
    try:
        return int(value)
    except:
        pass
    try:
        return float(value)
    except:
        pass
    return value


def to_dict(value):
    try:
        return json.loads(value)
    except:
        pass
    return value


def csv_to_json(csv_path, json_path):

    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        json_data = list(reader)

    json_data = json.loads(
        json.dumps(json_data, ensure_ascii=False, sort_keys=False),
    )

    res = []
    for item in json_data:
        new_item = {}
        for key in item:
            item[key] = to_numeric(item[key])
            item[key] = to_dict(item[key])
            trim_key = re.match(r"^\s*(.*?)\s*$", key).group(1).strip()
            remove_unicode_key = re.sub(r"[\u200b-\u200d\uFEFF]", "", trim_key)
            new_item[remove_unicode_key] = item[key]
        res.append(new_item)

  
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(
            res,
            f,
            ensure_ascii=False,
            indent=4,
            sort_keys=False,
        )



def main(csv_file_path, json_file_path):
  
    if not Path(csv_file_path).is_file():
        print(f"Error: The file '{csv_file_path}' does not exist.")
        sys.exit(1)

    try:
        
        if not json_file_path:
            json_file_path = csv_file_path.replace(".csv", ".json")
        
        csv_to_json(csv_file_path, json_file_path)
        
        print(f"Successfully converted '{csv_file_path}' to '{json_file_path}'.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print("Usage: python script.py <csv_file_path> <json_file_path>")
        sys.exit(1)

    
    csv_file_path = sys.argv[1]
    json_file_path = sys.argv[2] if len(sys.argv) == 3 else None

 
    main(csv_file_path, json_file_path)