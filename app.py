import os
import sys
import subprocess
import streamlit as st

st.set_page_config(page_title="BD Legal RAG Assistant", page_icon="⚖️")


def database_ready():
    """Check if the vector database actually exists AND has data in it."""
    if not os.path.exists("./chroma_db"):
        return False
    try:
        import chromadb
        client = chromadb.PersistentClient(path="./chroma_db")
        collection = client.get_collection("bd_legal_docs")
        return collection.count() > 0
    except Exception:
        return False


if not database_ready():
    with st.spinner("First-time setup: building document database... this may take a minute."):
        result = subprocess.run(
            [sys.executable, "build_database.py"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            st.error(f"Database build failed:\n{result.stderr}")
            st.stop()



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