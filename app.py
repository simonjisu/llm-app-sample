import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Appilcations",
    page_icon="👋",
)
st.write("# Welcome to Demo! 👋")
st.sidebar.success("Select a demo above.")
st.write("""
This document serves only as a quick guide for students in the Project4DS course to start learning development on top of ChatGPT and other LLM alike as well as an overview for approaches available and their target scenarios.          
The document will be updated continuously as new features are introduced. 
         
* Course Instructor: Wen-Syan Li(📬wensyanli@gmail.com)
* Created by: Jisoo Jang(📬simonjisu@gmail.com)
""")