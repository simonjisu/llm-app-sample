import streamlit as st
import requests

st.set_page_config(page_title="Financial Stock QA", page_icon="📈")

API_URL = "http://localhost:8000"

st.title("Financial Stock QA System")
clear_all_messages = st.sidebar.button("Clear all messages")
if clear_all_messages:
    st.session_state.messages = []

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Enter a message..."):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Ger assistant response from API
    response = requests.post(f"{API_URL}/financial_qa", json={"query": prompt})
    response = response.json()['response']['output']
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})