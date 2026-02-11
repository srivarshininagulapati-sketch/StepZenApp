# app.py

import streamlit as st
from google.genai import Client  # Use the new google.genai package

# =========================
# App Title & Creator Name
# =========================
st.title("My AI Chatbot + Habits Tracker")
st.markdown("Created by **Sri Varshini Nagulapati**")

# =========================
# Secrets & API Key Setup
# =========================
# Make sure you have .streamlit/secrets.toml with:
# GOOGLE_API_KEY = "your_gemini_api_key"
client = Client(api_key=st.secrets["GOOGLE_API_KEY"])

# =========================
# Sidebar: Habits Tracker
# =========================
st.sidebar.header("Habits Tracker")

# Example habits
habits = ["Exercise", "Read", "Meditate", "Coding"]
habit_status = {}

for habit in habits:
    habit_status[habit] = st.sidebar.checkbox(habit)

st.sidebar.write("Your daily habit status:")
for h, done in habit_status.items():
    st.sidebar.write(f"- {h}: {'✅ Done' if done else '❌ Not done'}")

# =========================
# Chatbot Section
# =========================
st.header("Ask me anything!")

if "messages" not in st.session_state:
    st.session_state.messages = []

user_input = st.text_input("Your question:")

if st.button("Send") and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Gemini API call
    try:
        response = client.chat.create(
            model="chat-bison-001",
            messages=st.session_state.messages
        )
        answer = response.last
        st.session_state.messages.append({"role": "assistant", "content": answer["content"]})
    except Exception as e:
        st.error(f"Error: {e}")

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Bot:** {msg['content']}")
