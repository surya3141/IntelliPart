import pandas as pd
import json

# Path to your JSONL file
jsonl_path = "01_dataset_expansion/01_dataset_expansion/production_dataset/shrunk_car_parts_dataset.jsonl"
# Output Excel file path
xlsx_path = "01_dataset_expansion/01_dataset_expansion/production_dataset/shrunk_car_parts_dataset.xlsx"

data = []
with open(jsonl_path, 'r', encoding='utf-8') as f:
    for line in f:
        data.append(json.loads(line))

df = pd.DataFrame(data)
df.to_excel(xlsx_path, index=False)
print(f"Exported to {xlsx_path}")
