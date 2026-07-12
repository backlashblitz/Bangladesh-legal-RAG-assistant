"""
STEP 4 SCRIPT (v2): Custom lightweight evaluation using Groq as judge.
Run this with: python run_eval.py
"""

from advanced_ask import ask, hybrid_search
from eval_data import test_cases
from groq import Groq
import json

import streamlit as st
import os

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY", "gsk_PASTE_YOUR_KEY_HERE"))
groq_client = Groq(api_key=GROQ_API_KEY)


def judge_answer(question, answer, context, ground_truth):
    """Ask the LLM to score faithfulness and relevance, 1-5 scale."""
    judge_prompt = f"""You are an evaluation judge. Score the AI answer below on two criteria.

Question: {question}

Retrieved Context (what the AI had access to):
{context}

AI's Answer: {answer}

Reference/Expected Answer: {ground_truth}

Score from 1-5 on each criterion:
- FAITHFULNESS: Is the AI's answer fully supported by the retrieved context (no made-up facts)? 5 = fully grounded, 1 = hallucinated/unsupported.
- RELEVANCE: Does the AI's answer actually address the question asked? 5 = directly answers it, 1 = off-topic.

Respond ONLY in this exact JSON format, nothing else:
{{"faithfulness": <number>, "relevance": <number>, "reasoning": "<one sentence explanation>"}}"""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": judge_prompt}],
    )

    raw = response.choices[0].message.content.strip()
    # Clean up in case the model wraps it in markdown code fences
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"faithfulness": None, "relevance": None, "reasoning": f"Could not parse: {raw}"}


print("Running evaluation...\n")

all_results = []
faithfulness_scores = []
relevance_scores = []

for case in test_cases:
    question = case["question"]
    print(f"Testing: {question}")

    answer, sources = ask(question)
    chunks, _ = hybrid_search(question)
    context = "\n\n".join(chunks)

    scores = judge_answer(question, answer, context, case["ground_truth"])

    print(f"  Faithfulness: {scores['faithfulness']}/5")
    print(f"  Relevance: {scores['relevance']}/5")
    print(f"  Reasoning: {scores['reasoning']}\n")

    if scores["faithfulness"] is not None:
        faithfulness_scores.append(scores["faithfulness"])
        relevance_scores.append(scores["relevance"])

    all_results.append({
        "question": question,
        "answer": answer,
        "sources": sources,
        **scores
    })

# ---- Summary ----
avg_faithfulness = sum(faithfulness_scores) / len(faithfulness_scores)
avg_relevance = sum(relevance_scores) / len(relevance_scores)

print("=" * 50)
print("EVALUATION SUMMARY")
print("=" * 50)
print(f"Average Faithfulness: {avg_faithfulness:.2f}/5")
print(f"Average Relevance: {avg_relevance:.2f}/5")
print(f"Total questions tested: {len(test_cases)}")

# Save detailed results to a file for your README
with open("eval_results.json", "w") as f:
    json.dump({
        "summary": {
            "avg_faithfulness": avg_faithfulness,
            "avg_relevance": avg_relevance,
            "total_questions": len(test_cases)
        },
        "details": all_results
    }, f, indent=2)

print("\nSaved detailed results to eval_results.json")