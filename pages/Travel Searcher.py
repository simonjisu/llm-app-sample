import streamlit as st
import requests
import time

def stream_output(sentence):
    for word in sentence.split(" "):
        yield word + " "
        time.sleep(0.02)

API_URL = "http://localhost:8000"
st.session_state.messages = []
st.set_page_config(page_title="Travel Searcher", layout="wide", page_icon="✈️")
st.write("Hi! I am a travel searcher. Please select the country and the city you want to visit. I'll help you to find hotels and restaurants at once.")

country_city = {
    "USA": ['New York', 'Los Angeles'],
    "France": ['Paris', 'Nice'],
    "Spain": ['Barcelona', 'Madrid'],
    "Japan": ['Tokyo', 'Osaka'],
    "China": ['Beijing', 'Shanghai'],
    "Korea": ['Seoul', 'Jeju']
}

col1, col2 = st.columns(2)
with col1:
    country = st.selectbox("Select a country", ["USA", "France", "Spain", "Japan", "China", "Korea"])
with col2:
    city = st.selectbox("Select a city", country_city[country])

if st.button("Search"):
    with st.spinner("Searching your trip..."):
        response = requests.post(f"{API_URL}/plan", json={"query": city})
        response = response.json()['response']
        
        hotel = response['hotel']
        restaurant = response['resturant']
        message = f"## Here are the hotels in {city}:\n"
        for i, h in enumerate(hotel):
            h_name = h["key"].rstrip(f"  {city}")
            h_res = h["result"]
            message += f"🏨 {i+1}. {h_name}\n"
            message += f"link: {h_res['link']}\n"
            message += f"{h_res['title']}. {h_res['snippet']}\n"

        message += f"\n## Here are the restaurants in {city}:\n"
        for i, r in enumerate(restaurant):
            r_name = r["key"].rstrip(f"  {city}")
            r_res = r["result"]
            message += f"🍽 {i+1}. {r_name}\n"
            message += f"link: {r_res['link']}\n"
            message += f"{r_res['title']}. {r_res['snippet']}\n"
        
        for sentence in message.split("\n"):
            st.write_stream(stream_output(sentence))