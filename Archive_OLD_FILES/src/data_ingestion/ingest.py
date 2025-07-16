import os
import pandas as pd
import json
import PyPDF2

def ingest_csv(file_path):
    return pd.read_csv(file_path).to_dict(orient='records')

def ingest_json(file_path):
    with open(file_path) as f:
        return json.load(f)

def ingest_txt(file_path):
    with open(file_path) as f:
        lines = f.readlines()
    # Custom parse logic required
    return [{"raw": line.strip()} for line in lines]

def ingest_pdf(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file '{file_path}' not found.")
    data = []
    with open(file_path, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                data.append({"raw": text})
    return data

def ingest(file_path):
    ext = os.path.splitext(file_path)[-1].lower()
    if ext == '.csv':
        return ingest_csv(file_path)
    elif ext == '.json':
        return ingest_json(file_path)
    elif ext == '.txt':
        return ingest_txt(file_path)
    elif ext == '.pdf':
        return ingest_pdf(file_path)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")