"""
Hybrid search (vector + keyword) + reranking + AI answer.
Can be run directly with: python advanced_ask.py
Or imported by app.py for the Streamlit UI.
"""

import os
import streamlit as st
from sentence_transformers import SentenceTransformer, CrossEncoder
from rank_bm25 import BM25Okapi
import chromadb
from groq import Groq

# ---- API key: works locally (.streamlit/secrets.toml) and on Streamlit Cloud (secrets) ----
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY", "gsk_PASTE_YOUR_KEY_HERE"))

print("Loading models... (this takes a moment)")
embed_model = SentenceTransformer("all-MiniLM-L6-v2")
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("bd_legal_docs")
groq_client = Groq(api_key=GROQ_API_KEY)

# ---- Load ALL chunks once, to build the keyword (BM25) index ----
print("Building keyword search index...")
all_data = collection.get(include=["documents", "metadatas"])
all_chunks = all_data["documents"]
all_metadatas = all_data["metadatas"]

tokenized_chunks = [chunk.lower().split() for chunk in all_chunks]
bm25 = BM25Okapi(tokenized_chunks)


def hybrid_search(question, vector_k=15, bm25_k=15, final_k=5):
    # ---- 1. Vector search ----
    q_embedding = embed_model.encode([question]).tolist()
    vector_results = collection.query(query_embeddings=q_embedding, n_results=vector_k)
    vector_chunks = vector_results["documents"][0]

    # ---- 2. Keyword (BM25) search ----
    tokenized_question = question.lower().split()
    bm25_scores = bm25.get_scores(tokenized_question)
    top_bm25_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:bm25_k]
    bm25_chunks = [all_chunks[i] for i in top_bm25_indices]

    # ---- 3. Combine and remove duplicates ----
    combined_chunks = list(dict.fromkeys(vector_chunks + bm25_chunks))  # preserves order, dedupes

    # ---- 4. Rerank the combined candidates ----
    pairs = [[question, chunk] for chunk in combined_chunks]
    rerank_scores = reranker.predict(pairs)

    # Sort chunks by rerank score, highest first
    reranked = sorted(zip(combined_chunks, rerank_scores), key=lambda x: x[1], reverse=True)
    top_chunks = [chunk for chunk, score in reranked[:final_k]]

    # ---- 5. Find which document (and section, if available) each top chunk came from ----
    sources = []
    for chunk in top_chunks:
        idx = all_chunks.index(chunk)
        meta = all_metadatas[idx]
        if meta.get("section_number"):
            sources.append(f"{meta['source']} (Section {meta['section_number']})")
        else:
            sources.append(meta["source"])

    return top_chunks, sources


def ask(question):
    chunks, sources = hybrid_search(question)
    context = "\n\n---\n\n".join(chunks)

    prompt = f"""You are a helpful assistant answering questions about Bangladeshi law.
Use ONLY the context below to answer. If the answer isn't in the context, say you don't know.
Read the context carefully, especially any conditions, dates, or numbers - do not misread them.

Context:
{context}

Question: {question}

Answer:"""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content, sources
    except Exception as e:
        return f"Sorry, something went wrong while generating the answer: {str(e)}", sources


if __name__ == "__main__":
    print("\n=== BD Legal RAG Assistant (Hybrid Search + Reranking) ===")
    print("Type your question, or 'quit' to exit.\n")

    while True:
        question = input("Your question: ")
        if question.lower() in ["quit", "exit"]:
            print("Bye!")
            break

        answer, sources = ask(question)
        print("\nANSWER:", answer)
        print("SOURCES:", sources)
        print("\n" + "-" * 50 + "\n")