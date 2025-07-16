# IntelliPart: Dataset Formatting, Fine-tuning, and RAG Guidance

## 1. Dataset Formatting for Best Semantic Search

- **Descriptive Fields:**
  - Use clear, specific values for each field. E.g., `"part_name": "Engine Mounting Bolt for XUV500"` instead of just `"Bolt"`.
- **Combine Context:**
  - If possible, add a `keywords` or `search_context` field that combines all relevant info: part name, description, system, manufacturer, synonyms, etc.
- **Avoid N/A/Empty:**
  - Remove or avoid fields with "N/A" or empty values.
- **Add Synonyms/Keywords:**
  - Add a `keywords` field with common alternate names or user search terms.
- **Sample Record:**
  ```json
  {
    "part_number": "123456",
    "part_name": "Engine Mounting Bolt for XUV500",
    "description": "High-tensile bolt used for mounting the engine in XUV500 models.",
    "system": "Engine",
    "manufacturer": "Bosch",
    "keywords": "mounting bolt, engine bolt, XUV500 bolt, Bosch bolt",
    "cost": "120",
    "stock": "50"
  }
  ```

## 2. Fine-tuning a SentenceTransformer (for better retrieval)

- **When to fine-tune:**
  - If your queries and dataset are very domain-specific and the default model doesn’t capture the relationships well.
- **How:**
  - Prepare pairs of (query, relevant record) and (query, irrelevant record) and use them to fine-tune the model using contrastive loss.
  - See: https://www.sbert.net/examples/training/quora_duplicate_questions/README.html
- **Script Outline:**
  - Collect real user queries and the correct matching part(s).
  - Use these as positive pairs. Sample random non-matching parts as negatives.
  - Use the SentenceTransformers library to fine-tune.

## 3. Retrieval-Augmented Generation (RAG) for True Q&A

- **What is RAG?**
  - RAG combines a retriever (your semantic search) with a generator (an LLM, e.g., OpenAI, Gemini, Llama). The retriever fetches relevant records, and the LLM synthesizes a natural-language answer using those records.
- **How to implement:**
  1. Use your current semantic search to fetch the top-k relevant records.
  2. Pass those records, along with the user’s query, as context to an LLM (e.g., OpenAI GPT, Gemini, or a local LLM).
  3. The LLM generates a natural-language answer, grounded in your data.
- **Open-source options:**
  - [Haystack](https://haystack.deepset.ai/) and [LlamaIndex](https://www.llamaindex.ai/) for RAG pipelines with open-source LLMs.
- **Cloud LLMs:**
  - Use OpenAI or Gemini APIs with a prompt that includes the retrieved records.

---

## Next Steps
- Improve your dataset as above for best search.
- If you want to fine-tune, collect query/answer pairs and use the SentenceTransformers fine-tuning guide.
- For RAG, you can add a function to your backend that, after retrieving top-k records, sends them (plus the user query) to an LLM for answer synthesis.

Let me know if you want a sample script for fine-tuning or a minimal RAG pipeline!
