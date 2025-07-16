import json
import random
import pandas as pd
from pathlib import Path

SERVICEABILITY = [
    "Not Required",
    "Production And Service",
    "Production Only",
    "Not Serviced Separately",
    "Service"
]
END_ITEMS = [
    "NA",
    "EI at Mahindra",
    "EI at Supplier - Procured by Supplier",
    "EI at Supplier - Procured by Mahindra",
    "EI at Supplier"
]
SOURCE = [
    "NA",
    "FSS",
    "BTP (Buy)",
    "Not Required",
    "BTP (Make)"
]

def load_hierarchy(csv_path):
    df = pd.read_csv(csv_path)
    # Use the correct column name from your CSV: "Sub Sub Sytem Name"
    df = df[["System Name", "Sub System Name", "Sub Sub Sytem Name"]].drop_duplicates()
    return df

def generate_shrunk_car_parts_dataset(output_file: str, num_records: int, csv_path: str):
    df = load_hierarchy(csv_path)
    systems = df.groupby("System Name")
    system_names = list(systems.groups.keys())
    records = []
    part_counter = 1

    while len(records) < num_records:
        system_name = random.choice(system_names)
        group = systems.get_group(system_name)
        row = group.sample(1).iloc[0]
        part_number = f"PN-{part_counter:05d}"
        part_description = f"{row['Sub Sub Sytem Name']} for {row['System Name']} > {row['Sub System Name']}"
        record = {
            "System Name": row["System Name"],
            "Sub System Name": row["Sub System Name"],
            # Output key as "Sub Sub System Name" for consistency, value from "Sub Sub Sytem Name"
            "Sub Sub System Name": row["Sub Sub Sytem Name"],
            "Serviceability": random.choice(SERVICEABILITY),
            "End Items": random.choice(END_ITEMS),
            "Source": random.choice(SOURCE),
            "Part Number": part_number,
            "Part Description": part_description
        }
        records.append(record)
        part_counter += 1

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"✅ Generated {num_records} records and saved to {output_file}")

if __name__ == "__main__":
    output_file = "01_dataset_expansion/production_dataset/shrunk_car_parts_dataset.jsonl"
    csv_path = "D:/OneDrive - Mahindra & Mahindra Ltd/Desktop/POC/Gemini/IntelliPart/IntelliPart/01_dataset_expansion/production_dataset/datasets/6 Attributes.csv"
    num_records = 500
    generate_shrunk_car_parts_dataset(output_file, num_records, csv_path)