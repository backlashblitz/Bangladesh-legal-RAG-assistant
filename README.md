# ⚖️ Bangladesh Legal RAG Assistant

> A domain-specific Retrieval-Augmented Generation (RAG) system that answers questions about Bangladeshi law using official government legal texts — built end-to-end with hybrid search, reranking, and systematic LLM-based evaluation.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🧠 What it does

Ask natural-language questions about Bangladeshi law — **Right to Information, Labour Rights, Consumer Protection, Anti-Corruption, and Income Tax** — and get grounded, source-cited answers pulled directly from the official acts, not from the LLM's general knowledge.

If the answer isn't in the source documents, the system says so instead of guessing — verified during evaluation with out-of-domain test questions.

**Example:**
> **Q:** What is the maternity benefit period for women workers?
> **A:** 8 weeks preceding delivery and 8 weeks following delivery, totaling 16 weeks.
> **📄 Source:** `labour-act-2006.pdf`

🔗 **[Live Demo](https://bangladesh-legal-rag-assistant.streamlit.app)**

---

## 🏗️ Architecture

```
User Question
      │
      ▼
┌──────────────────┐     ┌───────────────────┐
│   Vector Search   │     │  BM25 Keyword      │
│   (semantic)      │     │  Search (exact)     │
└─────────┬─────────┘     └─────────┬───────────┘
          └───────────┬─────────────┘
                       ▼
              Combined Candidates
                       │
                       ▼
             Cross-Encoder Reranker
                       │
                       ▼
              Top-K Relevant Chunks
                       │
                       ▼
             Groq LLM (Llama 3.3 70B)
                       │
                       ▼
             Grounded Answer + Sources
```
---

## 🛠️ Tech Stack

| Component | Tool | Why |
|---|---|---|
| Embeddings | `sentence-transformers` (all-MiniLM-L6-v2) | Free, local, no API limits |
| Vector store | ChromaDB | Free, persistent, zero setup |
| Keyword search | BM25 (`rank_bm25`) | Catches exact-term matches vector search misses |
| Reranking | Cross-Encoder (`ms-marco-MiniLM-L-6-v2`) | Improves precision of top results |
| LLM | Groq (Llama 3.3 70B) | Free tier, fast inference |
| UI | Streamlit | Fast to build, easy to deploy free |
| Evaluation | Custom LLM-as-judge harness | Faithfulness + relevance scoring |

---

## 📚 Data Sources

5 official Bangladeshi acts, sourced from [bdlaws.minlaw.gov.bd](http://bdlaws.minlaw.gov.bd) and the FAO legal database:

- Right to Information Act, 2009
- Bangladesh Labour Act, 2006
- Consumers' Right Protection Act, 2009
- Anti-Corruption Commission Act, 2004
- Income Tax Act, 2023

---

## 📊 Evaluation Results

Evaluated on a 5-question test set spanning all 5 legal domains, using an LLM-as-judge approach (Groq scoring faithfulness and relevance on a 1-5 scale):

| Metric | Score |
|---|---|
| **Faithfulness** | 4.80 / 5 |
| **Relevance** | 4.40 / 5 |

Full breakdown in [`eval_results.json`](./eval_results.json).

### Known limitation

Retrieval occasionally underranks the correct chunk when query phrasing diverges from source terminology (e.g. "file a complaint" vs. the source's "lodge a complaint"). Diagnosed via manual chunk inspection — confirmed the correct section exists cleanly in the vector store but scores below threshold with the free embedding/reranker models used here. A larger embedding model (e.g. OpenAI `text-embedding-3-large` or Cohere) would likely close this gap at added inference cost.

---

## 🚀 Setup

1. Clone this repo and install dependencies:
```bash
git clone https://github.com/backlashblitz/Bangladesh-legal-RAG-assistant.git
cd Bangladesh-legal-RAG-assistant
pip install -r requirements.txt
```

2. Get a free API key at [console.groq.com](https://console.groq.com).

3. Create `.streamlit/secrets.toml` and add:
```toml
GROQ_API_KEY = "your_key_here"
```

4. Build the vector database:
```bash
python build_database.py
```

5. Run the web app:
```bash
streamlit run app.py
```

---

## 📁 Project Structure

```
Bangladesh-legal-RAG-assistant/
├── data/raw_pdfs/          # Source legal PDFs
├── build_database.py       # Ingestion: PDF → chunks → embeddings → ChromaDB
├── advanced_ask.py         # Hybrid search + reranking RAG pipeline
├── app.py                  # Streamlit web UI
├── eval_data.py             # Test question set with ground truths
├── run_eval.py              # LLM-as-judge evaluation harness
├── eval_results.json        # Evaluation output
├── requirements.txt
└── README.md
```
## 🔮 Future Improvements

- Expand document coverage to more citizen-service laws
- Experiment with paid embedding models to address the known retrieval limitation
- Add conversation memory for multi-turn follow-up questions
- Add automated regression tests for retrieval quality

---


