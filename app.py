import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.title("Financial QA System for a Single Ticker")
ticker = st.sidebar.selectbox("Ticker Info", ["AAPL", "GOOGL", "AMZN", "MSFT"])
query = st.chat_input("type your question here")
# TODO: implement chat history

if query:
    st.write(f"Question: {query}")
    response = requests.post(f"{API_URL}/qa", json={"query": query})
    response = response.json()['response']['content']
    st.write(f"Response: {response}")


