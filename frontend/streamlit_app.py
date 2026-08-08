# Frontend for TiMESS - Streamlit app
import os
import uuid

import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="TiMESS", page_icon=":dna:")
st.title("TiMESS")
st.caption("Your spatial biology & single-cell platform expert")

if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if question := st.chat_input("Ask about Flex, Visium HD, Xenium..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            resp = requests.post(
                f"{BACKEND_URL}/api/chat",
                json={
                    "user_id": st.session_state.user_id,
                    "query": question,
                    "session_id": st.session_state.session_id,
                },
                timeout=120,
            )
            data = resp.json()
            st.session_state.session_id = data["session_id"]
            st.markdown(data["answer"])

    st.session_state.messages.append({"role": "assistant", "content": data["answer"]})