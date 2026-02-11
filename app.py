import streamlit as st
import json
from google.genai import Client
import os

# Initialize Gemini client
client = Client(api_key=st.secrets["GOOGLE_API_KEY"])

st.title("My First Chatbot App")

# File to save habits/questions
HABITS_FILE = ".streamlit/habits.json"

# Load previous habits from file
if os.path.exists(HABITS_FILE):
    with open(HABITS_FILE, "r") as f:
        st.session_state.history = json.load(f)
else:
    st.session_state.history = []

# Input box
question = st.text_input("Ask a question:")

if question:
    # Call Gemini API
    response = client.generate_text(
        model="chat-bison-001",
        prompt=question,
        temperature=0.7,
        max_output_tokens=256
    )

    # Save Q&A to session
    st.session_state.history.append({"question": question, "answer": response.text})

    # Save to file permanently
    with open(HABITS_FILE, "w") as f:
        json.dump(st.session_state.history, f, indent=2)

# Display all previous Q&A
for chat in st.session_state.history:
    st.markdown(f"**You:** {chat['question']}")
    st.markdown(f"**Bot:** {chat['answer']}")
