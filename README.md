# ⚖️ Bangladesh Legal RAG Assistant

> A domain-specific Retrieval-Augmented Generation (RAG) system that answers questions about Bangladeshi law using official government legal texts — built end-to-end with hybrid search, reranking, and systematic LLM-based evaluation.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🧠 What it does

Ask natural-language questions about Bangladeshi law — **Right to Information, Labour Rights, Consumer Protection, Anti-Corruption, Income Tax, Births and Deaths Registration, and Citizenship Act** — and get grounded, source-cited answers pulled directly from the official acts, not from the LLM's general knowledge.

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

7 official Bangladeshi acts, sourced from [bdlaws.minlaw.gov.bd](http://bdlaws.minlaw.gov.bd) and other official sources:

- Right to Information Act, 2009
- Bangladesh Labour Act, 2006
- Consumers' Right Protection Act, 2009
- Anti-Corruption Commission Act, 2004
- Income Tax Act, 2023
- Births and Deaths Registration Act, 2004
- Citizenship Act, 1951

---

## 📊 Evaluation Results

Evaluated on a 16-question test set spanning all 5 legal domains plus an out-of-domain guardrail check, using an LLM-as-judge approach (Groq scoring faithfulness and relevance on a 1-5 scale):

| Metric | Score |
|---|---|
| **Faithfulness** | 4.88 / 5 |
| **Relevance** | 4.25 / 5 |

Full breakdown in [`eval_results.json`](./eval_results.json).

**Note on structure-aware chunking:** switching from fixed-size to legal-section-boundary chunking improved faithfulness (4.75 → 4.88) — answers are more consistently grounded in complete, well-formed legal sections rather than arbitrary text windows. However, relevance saw a slight dip (4.56 → 4.25), likely because long sections that get sub-chunked can separate a section's identifying opening text from its later detail, occasionally causing the most relevant fragment to rank lower. This is a real tradeoff of structure-aware chunking, not an unambiguous improvement.

### Known limitations

1. **Paraphrase gap:** Retrieval occasionally underranks the correct chunk when query phrasing diverges from source terminology, even when the chunk itself is clean and well-formed. Confirmed via structure-aware chunking (splitting by legal section boundaries): the RTI Act's complaint procedure (Section 25) exists as a complete, well-structured chunk in the vector store, but still scores below the top-5 threshold for "file a complaint" vs. the source's "lodge a complaint." This isolates the issue to the embedding/reranking model's semantic sensitivity, not chunk quality.

2. **Cross-document keyword collision:** Asking about a product "refund" can surface Income Tax Act chunks (which discuss tax refunds) alongside relevant Consumer Rights Act chunks, since BM25 matches the literal word regardless of legal context. A document-classification approach (boosting chunks from the most semantically likely document) was tested and successfully fixed this specific case, but measurably reduced overall answer relevance (4.56 → 4.06 across the evaluation set) by over-promoting less-relevant chunks within the "boosted" document. This was reverted after evaluation — a useful finding that a targeted fix for one failure mode can regress others, and that fixed-strength heuristic boosts are risky without more careful tuning or a held-out validation set.

1. **Paraphrase gap:** "file a complaint" vs. the source's "lodge a complaint" — the correct RTI Act section exists cleanly in the vector store but scores below threshold in reranking.
2. **Cross-document keyword collision:** asking about a product "refund" pulls in Income Tax Act chunks (which discuss tax refunds) alongside the relevant Consumer Rights Act chunks, because BM25 keyword search matches the literal word "refund" regardless of legal context.

Both stem from the same root cause: the free, local embedding/reranker models used here (chosen for zero-cost deployment) are less robust to phrasing variation and cross-domain word collisions than larger paid models. A production system would likely use a larger embedding model (e.g. OpenAI `text-embedding-3-large` or Cohere) and/or weight BM25 keyword matches by relevance score rather than raw term frequency, at added inference cost.



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


