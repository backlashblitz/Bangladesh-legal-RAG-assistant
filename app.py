"""
Streamlit web UI for the BD Legal RAG Assistant.
Run with: streamlit run app.py
"""

import os
import subprocess
import streamlit as st

st.set_page_config(page_title="BD Legal RAG Assistant", page_icon="⚖️")

# ---- First-time setup: build the vector database if it doesn't exist yet ----
if not os.path.exists("./chroma_db"):
    with st.spinner("First-time setup: building document database... this may take a minute."):
        subprocess.run(["python", "build_database.py"])

from advanced_ask import ask  # imported after the DB check above

st.title("⚖️ BD Legal RAG Assistant")
st.caption("Ask questions about Bangladeshi law — Right to Information, Labour, Consumer Rights, Anti-Corruption, and Income Tax")

# Keep chat history across interactions
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show past messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg["role"] == "assistant" and msg.get("sources"):
            answer_text = msg["content"].lower()
            if "i don't know" not in answer_text and "cannot" not in answer_text:
                st.caption(f"📄 Sources: {', '.join(set(msg['sources']))}")

# Input box
question = st.chat_input("Ask a question about Bangladeshi law...")

if question:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    # Get answer
    with st.chat_message("assistant"):
        with st.spinner("Searching legal documents..."):
            try:
                answer, sources = ask(question)
            except Exception as e:
                answer = "Something went wrong processing your question. Please try again."
                sources = []
                st.error(f"Debug info: {str(e)}")

        st.write(answer)
        if sources and "i don't know" not in answer.lower() and "cannot" not in answer.lower():
            st.caption(f"📄 Sources: {', '.join(set(sources))}")

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources
    })