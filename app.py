import streamlit as st
import json
import os
from google import genai

# Configure API key
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

# ---------- App Title ----------
st.title("Hello Varshini 💖")
st.write("My first Streamlit app 🚀")

# ---------- Habit Tracker ----------
st.subheader("🌟 Habit Tracker")

# File to save habits
habits_file = "habits.json"
if os.path.exists(habits_file):
    with open(habits_file, "r") as f:
        habits = json.load(f)
else:
    habits = []

# Input habit
habit = st.text_input("Enter a habit")

if st.button("Add Habit"):
    if habit:
        habits.append(habit)
        with open(habits_file, "w") as f:
            json.dump(habits, f)
        st.success(f"{habit} added successfully! ✅")
    else:
        st.error("Please enter a habit!")

# Show all habits
if habits:
    st.write("Your habits so far:")
    for h in habits:
        st.write(f"- {h}")

# ---------- Chatbot ----------
st.subheader("🤖 AI Chatbot")

# File to save chat history
chat_file = "chat_history.json"
if os.path.exists(chat_file):
    with open(chat_file, "r") as f:
        chat_history = json.load(f)
else:
    chat_history = []

# Input user question
user_input = st.text_input("Ask something...")

if st.button("Ask AI"):
    if user_input:
        try:
            # Gemini API call
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_input,
            )
            answer = response.text
        except Exception as e:
            if "RESOURCE_EXHAUSTED" in str(e):
                answer = "⚠️ Quota exceeded! Please try again tomorrow."
            else:
                answer = f"Error: {e}"

        # Save chat
        chat_history.append({"user": user_input, "ai": answer})
        with open(chat_file, "w") as f:
            json.dump(chat_history, f)

        # Display chat
        st.write(answer)
    else:
        st.error("Please enter a question before asking.")

# Show previous chat history
if chat_history:
    st.write("💬 Chat History:")
    for chat in chat_history:
        st.write(f"**You:** {chat['user']}")
        st.write(f"**AI:** {chat['ai']}")
    if st.button("Clear Chat History"):
        chat_history = []
        with open(chat_file, "w") as f:
            json.dump(chat_history, f)
        st.success("Chat history cleared!")

# ---------- Creator Info ----------
st.subheader("👤 Creator Info")

if st.button("Who created you?"):
    st.info("This chatbot was created by Sri Varshini Nagulapati 💖")
