# IntelliPart MVP Alignment Plan

## Goal
- Deliver an intelligent, scalable, and extensible auto parts search prototype by Wednesday.

## Approach

### Version 1 (Target: Monday)
- Deploy ElasticSearch, ingest up to 5000 parts as JSON (key-value) docs.
- Provide Python scripts for indexing and keyword search.
- Demo: Search by part/system/attribute in <1s.

### Version 2 (Target: Wednesday)
- Add semantic search: convert part rows to vectors (OpenAI embeddings or sentence-transformers).
- Store vectors (ElasticSearch dense_vector or Qdrant/FAISS).
- Implement: 
  - Similarity search by description
  - Auto-correct and suggestion (fuzzy or vector-based)
- Demo: Streamlit app for search with suggestions.

## Why GenAI?
- Classic search is enough for small, structured data.
- Semantic/AI search enables “find similar”, typo tolerance, and richer UX.

## Tech Stack
- ElasticSearch
- Python (elasticsearch-py, sentence-transformers, OpenAI)
- Streamlit (for UI)
- (Optional) Qdrant/FAISS for advanced vector search

## Timeline
- **Friday–Monday:** ElasticSearch MVP (classic search)
- **Monday–Wednesday:** Semantic search & Streamlit demo

## Ready for Feedback & Incremental Extension!