"""
DEBUG SCRIPT: See exactly what chunks get retrieved for a specific question.
"""

from advanced_ask import hybrid_search

question = "How can a person file a complaint under the RTI Act?"

chunks, sources = hybrid_search(question)

print(f"Question: {question}\n")
for i, (chunk, source) in enumerate(zip(chunks, sources)):
    print(f"--- Chunk {i+1} (from {source}) ---")
    print(chunk[:200] + "...\n")