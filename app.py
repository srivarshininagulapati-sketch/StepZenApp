import streamlit as st
import json
from google import genai
import os

# Configure Gemini API key
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

st.title("Hello Varshini 💖")
st.write("My first Streamlit app 🚀")

# -------------------- HABITS TRACKER --------------------
st.subheader("🌟 Habit Tracker")

# Load existing habits
habits_file = "habits.json"
if os.path.exists(habits_file):
    with open(habits_file, "r") as f:
        habits = json.load(f)
else:
    habits = []

# Display habits
for i, h in enumerate(habits):
    st.write(f"{i+1}. {h}")

# Add new habit
habit = st.text_input("Enter a habit")

if st.button("Add Habit"):
    if habit:
        habits.append(habit)
        with open(habits_file, "w") as f:
            json.dump(habits, f)
        st.success(f"Habit '{habit}' added successfully! ✅")
        st.experimental_rerun()
    else:
        st.error("Please enter a habit!")

# -------------------- AI CHATBOT --------------------
st.subheader("🤖 AI Chatbot")

# Load chat history
chat_file = "chat_history.json"
if os.path.exists(chat_file):
    with open(chat_file, "r") as f:
        chat_history = json.load(f)
else:
    chat_history = []

# Display chat history
st.write("### Chat History")
for chat in chat_history:
    st.write(f"**You:** {chat['question']}")
    st.write(f"**AI:** {chat['answer']}")
    st.write("---")

# User input
user_input = st.text_input("Ask something...")

if st.button("Ask AI"):
    if user_input:
        try:
            # Special case: creator question
            if "who created you" in user_input.lower():
                answer = "I was created by Sri Varshini Nagulapati 💖"
            else:
                # Call Gemini AI for other questions
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=user_input
                )
                answer = response.text

            # Save chat
            chat_history.append({"question": user_input, "answer": answer})
            with open(chat_file, "w") as f:
                json.dump(chat_history, f)

            st.success("Chat saved successfully!")
            st.experimental_rerun()  # Refresh to show updated chat

        except Exception as e:
            st.error(f"Error: {e}")

# Option to clear chat history
if st.button("Clear Chat History"):
    chat_history = []
    if os.path.exists(chat_file):
        os.remove(chat_file)
    st.success("Chat history cleared!")
    st.experimental_rerun()
