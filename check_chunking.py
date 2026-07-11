"""
DEBUG: Check if Section 25 (RTI complaint procedure) exists as a clean chunk.
"""

import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("bd_legal_docs")

all_data = collection.get(include=["documents", "metadatas"])

for doc, meta in zip(all_data["documents"], all_data["metadatas"]):
    if meta["source"] == "rti-act-2009.pdf" and "Making of Complaint" in doc:
        print(f"--- Found in chunk {meta['chunk_index']} ---")
        print(doc)
        print()