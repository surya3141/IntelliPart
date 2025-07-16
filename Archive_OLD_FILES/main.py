from IntelliPart.src.data_ingestion import ingest
from IntelliPart.src.vectorization.vectorize import vectorize_records

if __name__ == "__main__":
    file_path = "data/sample_parts.csv"
    records = ingest(file_path)
    vectors = vectorize_records(records, text_field="raw")
    print(f"Ingested and vectorized {len(records)} records.")