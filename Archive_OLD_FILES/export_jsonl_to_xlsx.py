import json
import pandas as pd

# Read the JSONL file
input_path = "synthetic_car_parts_500.jsonl"
output_path = "synthetic_car_parts_500.xlsx"

records = []
with open(input_path, "r", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            records.append(json.loads(line.strip()))

# Convert to DataFrame and export to Excel
if records:
    df = pd.DataFrame(records)
    df.to_excel(output_path, index=False)
    print(f"Exported {len(df)} records to {output_path}")
else:
    print("No records found in JSONL file.")
