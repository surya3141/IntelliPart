"""
Sample: Fine-tuning and RAG for IntelliPart

This script provides:
1. A template for fine-tuning a SentenceTransformer on your own query/part pairs.
2. A minimal RAG pipeline using OpenAI (or any LLM API) for answer synthesis.

Requirements:
    pip install sentence-transformers openai
"""

# 1. Fine-tuning SentenceTransformer

from sentence_transformers import SentenceTransformer, InputExample, losses, models
from torch.utils.data import DataLoader
import random
import json

# Prepare your data: list of (query, relevant_part_text)
positive_pairs = [
    ("Show me brake pads for XUV500", "Brake Pad for XUV500, Bosch, Engine, ..."),
    # ... add more real user queries and matching part descriptions ...
]

# Optionally, add negative pairs (query, irrelevant_part_text)
all_part_texts = [p[1] for p in positive_pairs]  # or from your dataset
negative_pairs = []
for query, pos in positive_pairs:
    neg = random.choice([t for t in all_part_texts if t != pos])
    negative_pairs.append((query, neg))

train_examples = [InputExample(texts=[q, p], label=1.0) for q, p in positive_pairs] + \
                 [InputExample(texts=[q, p], label=0.0) for q, p in negative_pairs]

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=8)
train_loss = losses.CosineSimilarityLoss(model)

# model.fit(train_objectives=[(train_dataloader, train_loss)], epochs=1, warmup_steps=10)
# model.save('fine_tuned_model')

# 2. Minimal RAG Pipeline (using OpenAI, can adapt to Gemini or Llama)
import openai
openai.api_key = 'YOUR_OPENAI_API_KEY'

def rag_answer(user_query, top_k_records):
    context = "\n".join([json.dumps(rec, ensure_ascii=False) for rec in top_k_records])
    prompt = (
        "You are an expert automotive parts assistant. Here is the dataset context:\n"
        f"{context}\n"
        f"User Query: {user_query}\n"
        "Answer the query using only the dataset context above. If you don't know, say so."
    )
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=256,
        temperature=0.2
    )
    return response['choices'][0]['message']['content']

# Usage:
# top_k = semantic_engine.search("Show me brake pads for XUV500", top_k=5)
# answer = rag_answer("Show me brake pads for XUV500", top_k)
# print(answer)

# 3. Advanced: Local LLM RAG (Offline, HuggingFace Transformers)
# Requires: pip install transformers torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch

def local_llm_rag_answer(user_query, top_k_records, model_name_or_path="microsoft/Phi-3-mini-4k-instruct"):
    """
    Use a local LLM (e.g., Phi-3, Llama, Mistral) for answer synthesis. Model must be downloaded locally.
    """
    context = "\n".join([json.dumps(rec, ensure_ascii=False) for rec in top_k_records])
    prompt = (
        "You are an expert automotive parts assistant. Here is the dataset context:\n"
        f"{context}\n"
        f"User Query: {user_query}\n"
        "Answer the query using only the dataset context above. If you don't know, say so."
    )
    device = 0 if torch.cuda.is_available() else -1
    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
    model = AutoModelForCausalLM.from_pretrained(model_name_or_path)
    pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, device=device)
    output = pipe(prompt, max_new_tokens=256, temperature=0.2)[0]['generated_text']
    # Post-process to extract only the answer
    answer = output.split("User Query:")[-1].split("Answer the query")[-1].strip() if "Answer the query" in output else output.strip()
    return answer

ADVANCED_PROMPT_TEMPLATE = (
    "You are Mahindra IntelliPart, an expert automotive parts assistant.\n"
    "Below is a sample of the dataset you have access to (JSONL format, each line is a part record):\n"
    "{context}\n"
    "User Query: {user_query}\n"
    "Instructions:\n"
    "- Analyze and understand the dataset structure and content.\n"
    "- Synthesize a helpful, context-aware answer using only the dataset context above.\n"
    "- If the query is ambiguous, ask clarifying questions or suggest next steps.\n"
    "- If you cannot answer, explain why and suggest what the user can try next.\n"
    "- Always be natural, helpful, and use the user's language.\n"
)

def advanced_rag_answer(user_query, top_k_records, llm_func, prompt_template=ADVANCED_PROMPT_TEMPLATE):
    context = "\n".join([json.dumps(rec, ensure_ascii=False) for rec in top_k_records])
    prompt = prompt_template.format(context=context, user_query=user_query)
    return llm_func(prompt)

# 5. Production Fine-tuning Guidance
#
# Production Fine-tuning Steps:
# 1. Collect real user queries and correct answers (query, answer) pairs.
# 2. Format as InputExample(texts=[query, answer], label=1.0) for positives.
# 3. Add negatives: (query, wrong_answer), label=0.0.
# 4. Train as above, but with more epochs and validation split.
# 5. Save model: model.save('fine_tuned_model')
# 6. Evaluate: Use semantic_engine.search() and compare top-1/top-3 accuracy against a held-out test set.
# 7. For RAG, use the fine-tuned model for semantic search, then pass top-k to your LLM (OpenAI, Gemini, or local).
