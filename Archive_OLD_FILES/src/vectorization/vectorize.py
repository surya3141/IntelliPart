from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def vectorize_records(records, text_field="raw"):
    texts = [rec[text_field] if text_field in rec else str(rec) for rec in records]
    return model.encode(texts, show_progress_bar=True)