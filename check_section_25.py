import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("bd_legal_docs")

all_data = collection.get(include=["documents", "metadatas"])

for doc, meta in zip(all_data["documents"], all_data["metadatas"]):
    if meta["source"] == "rti-act-2009.pdf" and meta.get("section_number") == "25":
        print(f"--- Sub-chunk (chunk_index {meta['chunk_index']}) ---")
        print(doc[:300])
        print()