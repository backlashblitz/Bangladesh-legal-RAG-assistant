"""
STEP 1 SCRIPT (v2): Structure-aware chunking.
Splits documents by legal section boundaries (e.g. "25. Making of Complaint")
instead of blind character windows, and stores section number/title as metadata.
Falls back to fixed-size chunking if no clear section pattern is found.

Run this with: python build_database.py
"""

import os
import re
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb

# Matches things like: "25. Making of Complaint, disposal, etc.⎯"
# Looks for a newline, then a number (1-4 digits), a period, then a capital-letter title.
SECTION_PATTERN = re.compile(r'\n\s*(\d{1,4})\.\s+([A-Z][^\n]{2,100})')

MAX_SECTION_CHARS = 1200   # if a section is longer than this, sub-chunk it
SUB_CHUNK_SIZE = 800
SUB_CHUNK_OVERLAP = 100
FALLBACK_CHUNK_SIZE = 800
FALLBACK_OVERLAP = 100


def extract_text_from_pdf(path):
    reader = PdfReader(path)
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"
    return full_text


def split_by_sections(text):
    """
    Returns a list of dicts: {"text": ..., "section_number": ..., "section_title": ...}
    Falls back to None values if no section markers are found at all.
    """
    matches = list(SECTION_PATTERN.finditer(text))

    # If we found very few section markers, this PDF probably didn't parse cleanly
    # enough for structure-aware splitting - signal fallback needed.
    if len(matches) < 3:
        return None

    sections = []
    for i, match in enumerate(matches):
        section_number = match.group(1)
        section_title = match.group(2).strip()
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        section_text = text[start:end].strip()
        if len(section_text) > 30:  # skip near-empty matches
            sections.append({
                "text": section_text,
                "section_number": section_number,
                "section_title": section_title
            })
    return sections


def sub_chunk_if_needed(section_text, section_number, section_title):
    """If a section is too long, split it further while keeping the same section metadata."""
    if len(section_text) <= MAX_SECTION_CHARS:
        return [{"text": section_text, "section_number": section_number, "section_title": section_title}]

    sub_chunks = []
    start = 0
    while start < len(section_text):
        end = start + SUB_CHUNK_SIZE
        chunk = section_text[start:end].strip()
        if len(chunk) > 50:
            sub_chunks.append({"text": chunk, "section_number": section_number, "section_title": section_title})
        start += SUB_CHUNK_SIZE - SUB_CHUNK_OVERLAP
    return sub_chunks


def fallback_chunk(text):
    """Old-style fixed-size chunking, used when section detection fails."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + FALLBACK_CHUNK_SIZE
        chunk = text[start:end].strip()
        if len(chunk) > 50:
            chunks.append({"text": chunk, "section_number": None, "section_title": None})
        start += FALLBACK_CHUNK_SIZE - FALLBACK_OVERLAP
    return chunks


print("Loading embedding model... (first time takes a minute)")
model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path="./chroma_db")
# Delete old collection if it exists, so we don't mix old flat chunks with new structured ones
try:
    client.delete_collection("bd_legal_docs")
    print("Cleared old collection to rebuild with structure-aware chunking.")
except Exception:
    pass
collection = client.get_or_create_collection("bd_legal_docs")

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

        sections = split_by_sections(text)

        if sections is None:
            print("  No clear section structure detected - using fallback chunking")
            raw_chunks = fallback_chunk(text)
        else:
            print(f"  Detected {len(sections)} legal sections")
            raw_chunks = []
            for sec in sections:
                raw_chunks.extend(sub_chunk_if_needed(sec["text"], sec["section_number"], sec["section_title"]))

        print(f"  Final chunk count: {len(raw_chunks)}")

        chunk_texts = [c["text"] for c in raw_chunks]
        embeddings = model.encode(chunk_texts).tolist()

        ids = [f"{filename}_{i}" for i in range(len(raw_chunks))]
        metadatas = []
        for i, c in enumerate(raw_chunks):
            meta = {"source": filename, "chunk_index": i}
            if c["section_number"]:
                meta["section_number"] = c["section_number"]
                meta["section_title"] = c["section_title"][:100]  # keep metadata values short
            metadatas.append(meta)

        collection.add(
            documents=chunk_texts,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas
        )
        print(f"  Saved to database!")

    print(f"\nDONE. Total chunks in database: {collection.count()}")