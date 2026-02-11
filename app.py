import streamlit as st
import json
import os
from google.genai import Client

# Load API key from Streamlit secrets
client = Client(api_key=st.secrets["GOOGLE_API_KEY"])

# File to store habits permanently
HABITS_FILE = "habits.json"

# Load existing habits
if os.path.exists(HABITS_FILE):
    with open(HABITS_FILE, "r") as f:
        habits_data = json.load(f)
else:
    habits_data = {"name": "", "habits": []}

# User input for name
name = st.text_input("Enter your name:", value=habits_data.get("name", ""))
habits_data["name"] = name

st.title("My First Chatbot App")
st.write(f"Welcome, {name}!")

# Input habit
new_habit = st.text_input("Add a habit:")
if st.button("Save habit") and new_habit:
    habits_data["habits"].append(new_habit)
    with open(HABITS_FILE, "w") as f:
        json.dump(habits_data, f)
    st.success(f"Habit '{new_habit}' saved!")

# Show saved habits
st.write("Your Habits:")
for h in habits_data.get("habits", []):
    st.write("- " + h)

# Chatbot interaction
user_question = st.text_input("Ask a question to the chatbot:")
if user_question:
    response = client.responses.create(
        model="models/text-bison-001",
        input=user_question
    )
    st.write("Chatbot:", response.output_text)
