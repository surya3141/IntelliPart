from sentence_transformers import SentenceTransformer
model = SentenceTransformer('./.model_cache/all-MiniLM-L6-v2')
print("Model loaded successfully!")