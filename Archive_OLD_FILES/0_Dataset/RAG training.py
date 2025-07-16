"""
Utility to load the shrunk_car_parts_dataset.jsonl file and prepare it for semantic search or RAG.

Usage:
    python load_parts_dataset.py

This script:
- Loads the dataset from JSONL.
- Combines all relevant fields into a single string for each part (for embedding/search).
- Prints a sample combined record.
"""

import json
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader
import random
import faiss

DATASET_PATH = r'd:\OneDrive - Mahindra & Mahindra Ltd\Desktop\POC\Gemini\IntelliPart\IntelliPart\0_Dataset\shrunk_car_parts_dataset.jsonl'

def load_parts_dataset(path=DATASET_PATH):
    parts = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            parts.append(json.loads(line))
    return parts

def part_to_text(part):
    # Combine all relevant fields for semantic search/RAG
    return " | ".join([
        part.get("Part Number", ""),
        part.get("Part Description", ""),
        part.get("System Name", ""),
        part.get("Sub System Name", ""),
        part.get("Sub Sub System Name", ""),
        part.get("Serviceability", ""),
        part.get("End Items", ""),
        part.get("Source", "")
    ])

# 1. Prepare positive and negative pairs for fine-tuning
parts = load_parts_dataset()
part_texts = [part_to_text(p) for p in parts]

# More diverse positive pairs for better generalization
positive_pairs = []
for p in parts[:20]:
    positive_pairs.append((f"Find part {p['Part Number']}", part_to_text(p)))
    positive_pairs.append((p["Part Number"], part_to_text(p)))
    positive_pairs.append((p["Part Description"], part_to_text(p)))
    positive_pairs.append(("Show all parts", part_to_text(p)))
    positive_pairs.append(("HI", part_to_text(p)))

# 10 selected recommended queries for RAG fine-tuning
recommended_queries = [
    "Find part PN-00500",
    "Show all drive half shaft tubes",
    "List all engine mounts",
    "Show storage tank for exhaust system",
    "Which parts are not serviced separately in trims?",
    "Show pedal and supports for brakes system",
    "List all controller cooling parts for electrical vehicle drive system",
    "What is the crankshaft part for engine system?",
    "Show hazard warning switches for lighting system",
    "List all parts for the BODY SYSTEM"
]

# Helper: find relevant parts for each query
for rq in recommended_queries:
    # Direct part number lookup
    if "PN-00500" in rq:
        for p in parts:
            if p.get("Part Number", "").strip().upper() == "PN-00500":
                positive_pairs.append((rq, part_to_text(p)))
    elif "drive half shaft tubes" in rq.lower():
        for p in parts:
            if "drive half shaft tubes" in p.get("Part Description", "").lower():
                positive_pairs.append((rq, part_to_text(p)))
    elif "engine mounts" in rq.lower():
        for p in parts:
            if "engine mounts" in p.get("Part Description", "").lower():
                positive_pairs.append((rq, part_to_text(p)))
    elif "storage tank" in rq.lower() and "exhaust system" in rq.lower():
        for p in parts:
            if "storage tank" in p.get("Part Description", "").lower() and "exhaust system" in p.get("System Name", "").lower():
                positive_pairs.append((rq, part_to_text(p)))
    elif "not serviced separately" in rq.lower() and "trims" in rq.lower():
        for p in parts:
            if "not serviced separately" in p.get("Serviceability", "").lower() and "trims" in p.get("System Name", "").lower():
                positive_pairs.append((rq, part_to_text(p)))
    elif "pedal and supports" in rq.lower() and "brakes system" in rq.lower():
        for p in parts:
            if "pedal and supports" in p.get("Part Description", "").lower() and "brakes system" in p.get("System Name", "").lower():
                positive_pairs.append((rq, part_to_text(p)))
    elif "controller cooling" in rq.lower() and "electrical vehicle drive system" in rq.lower():
        for p in parts:
            if "controller cooling" in p.get("Sub System Name", "").lower() and "electrical vehicle drive system" in p.get("System Name", "").lower():
                positive_pairs.append((rq, part_to_text(p)))
    elif "crankshaft" in rq.lower() and "engine system" in rq.lower():
        for p in parts:
            if "crankshaft" in p.get("Part Description", "").lower() and "engine system" in p.get("System Name", "").lower():
                positive_pairs.append((rq, part_to_text(p)))
    elif "hazard warning switches" in rq.lower() and "lighting system" in rq.lower():
        for p in parts:
            if "hazard warning switches" in p.get("Part Description", "").lower() and "lighting system" in p.get("System Name", "").lower():
                positive_pairs.append((rq, part_to_text(p)))
    elif "body system" in rq.lower():
        for p in parts:
            if "body system" in p.get("System Name", "").lower():
                positive_pairs.append((rq, part_to_text(p)))

# Negative pairs: pair each query with a random wrong part
negative_pairs = []
for q, pos in positive_pairs:
    neg_part = random.choice([t for t in part_texts if t != pos])
    negative_pairs.append((q, neg_part))

train_examples = [InputExample(texts=[q, p], label=1.0) for q, p in positive_pairs] + \
                 [InputExample(texts=[q, p], label=0.0) for q, p in negative_pairs]

# 2. Fine-tune the model (quick demo: 1 epoch, use more for real training)
# IMPORTANT: Load the base model for training, then save to fine-tuned path
BASE_MODEL_PATH = r'C:\Users\25028489\all-MiniLM-L6-v2'  # Path to the downloaded base model
FINE_TUNED_MODEL_PATH = r'0_Dataset/fine_tuned_model'  # Path to save the fine-tuned model in project folder
model = SentenceTransformer(BASE_MODEL_PATH)
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=8)
train_loss = losses.CosineSimilarityLoss(model)
model.fit(train_objectives=[(train_dataloader, train_loss)], epochs=1, warmup_steps=10)
model.save(FINE_TUNED_MODEL_PATH)

# 3. Build FAISS search index
embeddings = model.encode(part_texts, convert_to_numpy=True, show_progress_bar=True)
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

# 4. Semantic search example
def semantic_search(query, top_k=5):
    query_emb = model.encode([query], convert_to_numpy=True)
    D, I = index.search(query_emb, top_k)
    return [parts[i] for i in I[0]]

# 5. (Optional) Local LLM RAG (if you want answer synthesis, e.g., with Phi-3, Llama, Mistral)
# from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
# def local_llm_rag_answer(user_query, top_k_records, model_name_or_path="microsoft/Phi-3-mini-4k-instruct"):
#     context = "\n".join([json.dumps(rec, ensure_ascii=False) for rec in top_k_records])
#     prompt = (
#         "You are an expert automotive parts assistant. Here is the dataset context:\n"
#         f"{context}\n"
#         f"User Query: {user_query}\n"
#         "Answer the query using only the dataset context above. If you don't know, say so."
#     )
#     tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
#     model = AutoModelForCausalLM.from_pretrained(model_name_or_path)
#     pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)
#     output = pipe(prompt, max_new_tokens=256, temperature=0.2)[0]['generated_text']
#     return output.strip()

if __name__ == "__main__":
    parts = load_parts_dataset()
    print(f"Loaded {len(parts)} parts.")
    if parts:
        print("Sample combined record for semantic search/RAG:")
        print(part_to_text(parts[0]))
    # Demo: semantic search
    query = "Find part PN-00500"
    top_k = semantic_search(query, top_k=3)
    print("Top semantic search results:")
    for p in top_k:
        print(part_to_text(p))
    # Uncomment below to use a local LLM for answer synthesis (if available)
    # print("\nLocal LLM RAG answer:")
    # print(local_llm_rag_answer(query, top_k))