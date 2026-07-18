"""
DEBUG SCRIPT: Check what chunks get retrieved for the shopkeeper refund question.
Run with: python debug_refund.py
"""

from advanced_ask import hybrid_search

question = "Can a shopkeeper refuse to give me a refund for a broken product?"

chunks, sources = hybrid_search(question)

print(f"Question: {question}\n")
print("=" * 60)

for i, (chunk, source) in enumerate(zip(chunks, sources)):
    print(f"\n--- Chunk {i+1} (from {source}) ---")
    print(chunk[:400])
    print()