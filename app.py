import streamlit as st
import json
import os
import google.genai as genai

# Gemini API Key
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

# Name
user_name = "Sri Varshini"

# Habits JSON file
if not os.path.exists("habits.json"):
    with open("habits.json", "w") as f:
        json.dump([], f)

# Load habits
with open("habits.json", "r") as f:
    habits = json.load(f)

st.title("My First Chatbot App")
st.write(f"Welcome, {user_name}!")

# Display habits
st.subheader("Your Habits")
for habit in habits:
    st.write("-", habit)

# Input new habit
new_habit = st.text_input("Add a new habit:")
if st.button("Save Habit") and new_habit:
    habits.append(new_habit)
    with open("habits.json", "w") as f:
        json.dump(habits, f)
    st.success(f"Habit '{new_habit}' saved!")

# Chatbot question
question = st.text_input("Ask a question:")
if st.button("Get Answer") and question:
    response = client.generate_text(
        model="text-bison-001",
        prompt=question
    )
    st.write("Answer:", response.text)
