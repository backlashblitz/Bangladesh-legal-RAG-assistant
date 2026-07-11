"""
STEP 2 SCRIPT: Ask a question -> search the database -> get an AI answer.
Run this with: python ask_question.py
"""

from sentence_transformers import SentenceTransformer
import chromadb
from groq import Groq

# ---- Paste your Groq API key here (between the quotes) ----
GROQ_API_KEY = "gsk_PASTE_YOUR_KEY_HERE"

# ---- Load the same embedding model used before ----
print("Loading model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# ---- Connect to your saved database ----
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("bd_legal_docs")

# ---- Connect to Groq (the free LLM) ----
groq_client = Groq(api_key=GROQ_API_KEY)


def ask(question, top_k=4):
    # 1. Turn the question into an embedding
    q_embedding = model.encode([question]).tolist()

    # 2. Search the database for the most relevant chunks
    results = collection.query(query_embeddings=q_embedding, n_results=top_k)
    chunks = results["documents"][0]
    sources = [m["source"] for m in results["metadatas"][0]]

    # 3. Build the context from those chunks
    context = "\n\n---\n\n".join(chunks)

    # 4. Ask the LLM to answer using only that context
    prompt = f"""You are a helpful assistant answering questions about Bangladeshi law.
Use ONLY the context below to answer. If the answer isn't in the context, say you don't know.

Context:
{context}

Question: {question}

Answer:"""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content, sources


if __name__ == "__main__":
    print("\n=== BD Legal RAG Assistant ===")
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