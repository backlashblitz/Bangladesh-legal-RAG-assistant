"""
STEP 1 SCRIPT: Read PDFs -> break into chunks -> save into a local database.
Run this with: python build_database.py
"""

import os
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb

# ---- 1. Read text out of every PDF in data/raw_pdfs ----
def extract_text_from_pdf(path):
    reader = PdfReader(path)
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"
    return full_text

# ---- 2. Break long text into small chunks (like paragraphs) ----
def split_into_chunks(text, chunk_size=800, overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if len(chunk) > 50:  # skip tiny useless chunks
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

# ---- 3. Load the free embedding model (downloads once, ~90MB) ----
print("Loading embedding model... (first time takes a minute)")
model = SentenceTransformer("all-MiniLM-L6-v2")

# ---- 4. Set up the local database ----
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("bd_legal_docs")

# ---- 5. Process every PDF in the folder ----
pdf_folder = "data/raw_pdfs"
pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")]

if not pdf_files:
    print("No PDF files found in data/raw_pdfs/ — put a PDF there first!")
else:
    for filename in pdf_files:
        print(f"\nProcessing: {filename}")
        full_path = os.path.join(pdf_folder, filename)

        text = extract_text_from_pdf(full_path)
        print(f"  Extracted {len(text)} characters")

        chunks = split_into_chunks(text)
        print(f"  Split into {len(chunks)} chunks")

        embeddings = model.encode(chunks).tolist()

        ids = [f"{filename}_{i}" for i in range(len(chunks))]
        metadatas = [{"source": filename, "chunk_index": i} for i in range(len(chunks))]

        collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas
        )
        print(f"  Saved to database!")

    print(f"\nDONE. Total chunks in database: {collection.count()}")