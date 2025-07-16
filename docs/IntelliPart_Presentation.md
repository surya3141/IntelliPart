````markdown
---
marp: true
theme: default
size: 16:9
paginate: true
---

# **IntelliPart: AI-Powered Parts Intelligence**
## **Accelerating Innovation & Reducing Costs at Mahindra**

**Presented By:** AI Assistant
**Date:** July 10, 2025

---

## **The Core Problem: The High Cost of Part Proliferation**

Mahindra faces a significant challenge that impacts our speed, cost, and sustainability goals.

*   **Duplicate Parts:** We frequently create new parts that are functionally identical to existing ones, leading to redundant design, testing, and inventory costs.
*   **Inconsistent Data:** Part descriptions are inconsistent, and critical technical attributes are often missing or incomplete.
*   **Inefficient Search:** Engineers lack an intelligent tool to search our vast parts database, leading to frustration and the default decision to create a new part.

**This "part proliferation" directly increases costs, lengthens design cycles, and hinders our ability to innovate at pace.**

---

## **🔍 Proposed AI Solution: IntelliPart**

### **✅ Solution Overview**

**IntelliPart is an AI-powered conversational platform that guides engineers to find and reuse existing parts quickly and confidently.**

It transforms parts discovery from a frustrating keyword search into an intelligent dialogue. By understanding user intent and technical context, it directly tackles the high costs of part proliferation, saving millions while accelerating time-to-market.

---

## **🎯 Key Features**

*   **Feature 1: Conversational & Semantic Search**
    Goes beyond keywords. IntelliPart understands the *meaning* behind a query (e.g., "durable brake pads for off-road use") to find conceptually similar parts, even with vague descriptions.

*   **Feature 2: Real-time Technical Filtering**
    Automatically extracts technical specifications like *"friction coefficient > 0.4"* or *"material: ceramic"* directly from the chat to deliver precise, filtered results instantly.

*   **Feature 3: RAG-Powered Intelligent Responses**
    It doesn't just list results. The AI provides a conversational summary, explains *why* parts match the query, and suggests next steps, powered by a secure, local Large Language Model (LLM).

---

## **🧠 AI Techniques & Technologies Used**

IntelliPart is powered by a modern, robust AI stack.

*   **Natural Language Processing (NLP):** The core for understanding user queries in a conversational manner.
*   **Semantic Search (Vector Search):** To find conceptually related parts, not just keyword matches.
    *   **Models:** `Sentence-Transformers` (fine-tuned for technical language)
    *   **Vector Database:** `FAISS` (for high-speed similarity search)
*   **Retrieval-Augmented Generation (RAG):** To generate intelligent, context-aware summaries without hallucination.
    *   **LLM:** `Ollama` running `Llama3` (ensuring data privacy and offline capability)
*   **Core Libraries:** `Python`, `Flask`, `PyTorch`, `HuggingFace Transformers`

---

## **🧩 System Architecture & Workflow**

**📌 High-Level Architecture**
```
User (Web UI)
     |
     v
Flask Backend API
     |
     v
[Query Parser (Regex)] -> [Semantic Search (FAISS)] -> [Filter Results] -> [LLM (Ollama RAG)]
     |
     v
Formatted Response (JSON)
     |
     v
User (Web UI)
```

---

## **🧩 System Architecture & Workflow**

**🔄 Workflow Steps**

1.  **Data Input:** An engineer types a natural language query (e.g., "Show me all-weather tires for a Thar") into the web chat interface.

2.  **Preprocessing & Inference:**
    *   The backend first **extracts key technical entities** ("all-weather", "tires", "Thar").
    *   The query is converted into a **vector embedding**.
    *   The `FAISS` vector index is searched to retrieve the **top N most similar parts**.
    *   These results are **filtered** based on the extracted entities.

3.  **Output & Feedback:**
    *   The final, filtered results are passed to the `Ollama` LLM, which generates a **conversational summary**.
    *   The UI displays the AI's summary, the top 5 matching parts, and **highlights the attributes** that matched the query, providing an explainable result.

---

## **📊 Dataset & Data Strategy**

*   **🔗 Data Sources:**
    The current model is built on a **synthetic dataset** (`synthetic_car_parts_500.jsonl`) that mirrors the structure and complexity of Mahindra's real-world parts database. This allows for rapid, safe development.

*   **📁 Type of Data:**
    **Semi-structured JSONL.** Each record contains a mix of structured fields (Part Number, Cost, Stock) and unstructured text fields (Part Description, System Name).

*   **🧹 Data Preprocessing:**
    During the indexing phase, all relevant text fields for each part are concatenated into a single string and then encoded into a vector embedding by the `Sentence-Transformer` model. This creates a rich representation for semantic search.

---

## **🤖 Model & Deployment Details**

*   **⚙️ Toolkit & Models:**
    *   **LLM:** `Ollama` with `Llama3` for private, secure natural language generation.
    *   **Embeddings:** `Sentence-Transformers` for creating vector representations of part data.
    *   **Vector Search:** `FAISS` for high-speed similarity search.
    *   **Backend:** `Flask` API serving the model and business logic.
    *   **Deployment Strategy:** The app is designed for future containerization with `Docker`.

*   **📈 Training & Performance:**
    *   **Dataset:** Trained on a synthetic dataset of `500` unique parts.
    *   **Fine-Tuning:** The embedding models are fine-tuned to understand technical jargon.
    *   **Performance:** Achieves fast, sub-second response times for most queries in the local environment.

---

## **💡 Innovation & Differentiation**

*   **What makes it innovative?**
    It's more than a search bar. It's a **conversational partner** that understands technical nuance. The use of a **local, private LLM (Ollama)** ensures data security and provides powerful RAG capabilities without external API calls.

*   **How does it stand out?**
    Unlike traditional PLM search tools that rely on rigid, structured queries, IntelliPart embraces the ambiguity of human language. It provides **explainable results**, showing users *why* a part is recommended, building trust and confidence.

---

## **🌍 Impact & Use Case Scenarios**

*   **👥 Target Users / Beneficiaries:**
    *   Design & Development Engineers
    *   Procurement & Sourcing Teams
    *   Quality Assurance & Testing Teams
    *   Service & Maintenance Staff

*   **💥 Expected Impact (Calculated):**
    *   **Productivity Savings:** **~₹8.3 Lakhs/month** by reducing search time from 30 mins to 5 mins.
    *   **Direct Cost Savings:** **~₹20 Lakhs/month** by preventing the creation of just 10 duplicate parts.
    *   **Total Estimated ROI:** **~₹28 Lakhs/month**.

---

## **🌐 Scalability & Future Roadmap**

IntelliPart is a foundational platform built for the future.

*   **Phase 1 (Q4 2025): Enhanced Recommendations**
    *   Implement **attribute-based similarity** scoring.
    *   Migrate search backend to **ElasticSearch** for enterprise-grade scalability.

*   **Phase 2 (Q1 2026): Proactive Integration**
    *   Develop **PLM/CAD plugins** (CATIA, Creo) to proactively suggest parts during the design phase.
    *   Integrate with **ERP systems** for real-time supply chain and cost data.

*   **Phase 3 (Q3 2026): Predictive & Generative AI**
    *   Use ML for **predictive analytics** on part performance and reliability.
    *   Introduce **Generative Design** to suggest modifications to *existing* parts to meet new requirements.

---

## **Thank You**

**Questions?**

````
