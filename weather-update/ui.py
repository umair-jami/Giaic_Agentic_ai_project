import streamlit as st
import asyncio
from main import run_weather_bot

# Session State Initialization
if "history" not in st.session_state:
    st.session_state.history=[]

st.set_page_config(page_title="WeatherBot 🌦️", page_icon="🌍", layout="centered")

# Light/Dark Mode Toggle
st.sidebar.title("⚙️ Settings")
theme = st.sidebar.radio("Theme", ("Dark", "Light"))

if theme == "Dark":
    st.markdown(
        """
        <style>
        body { background-color: #1e1e1e; color: #f0f0f0; }
        .stTextInput>div>div>input { background-color: #333; color: white; }
        div.stButton > button {
            background-color: #333333;
            color: white;
            border: 2px solid #555;
            padding: 10px 16px;
            border-radius: 10px;
        }
        div.stButton > button:hover {
            background-color: #444444;
            color: #FFD700;
            border-color: #FFD700;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        """
        <style>
        html, body, .stApp {
            background-color: #ffffff;
            color: black;
        }
         div.stButton > button {
            background-color: #f0f0f0;
            color: #333333;
            border: 2px solid #ccc;
            padding: 10px 16px;
            border-radius: 10px;
        }
        div.stButton > button:hover {
            background-color: #e0e0e0;
            color: #0066cc;
            border-color: #0066cc;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

st.title("🌤️ WeatherBot - Real-Time Weather Checker")
st.markdown("Get live weather updates using **OpenAI Agent SDK** & **OpenWeather API**.\n")

city=st.text_input("Enter a city name:", placeholder="e.g., New York, London, Karachi")

if st.button("Get Weather"):
    if city:
        with st.spinner("Fetching weather data..."):
            result = asyncio.run(run_weather_bot(city))
            st.success(result)
            keywords = {
                "cloud": "☁️", "rain": "🌧️", "clear": "☀️",
                "thunderstorm": "⛈️", "snow": "❄️", "mist": "🌫️"
            }
            icon="🌡️"
            for key,value in keywords.values():
                if key in result.lower():
                    icon =value
                    break
            st.markdown(f"### Weather Icon: {icon}")

            st.session_state.history.insert(0, f"{icon} **{city.title()}** → {result}")
    else:
        st.warning("⚠️ Please enter a city name.")
        
if st.session_state.history:
    st.markdown("## 📜 Query History")
    for item in st.session_state.history[:5]:
        st.markdown(f"- {item}")