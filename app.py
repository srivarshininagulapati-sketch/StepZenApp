import streamlit as st
from google import genai
import json
import os

# Configure API key
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

st.title("Hello Varshini 💖")
st.write("My first Streamlit app 🚀")

# ----------------- Habit Tracker -----------------
st.subheader("🌟 Habit Tracker")
habit_file = "habits.json"

# Load habits
if os.path.exists(habit_file):
    with open(habit_file, "r") as f:
        habits = json.load(f)
else:
    habits = []

habit = st.text_input("Enter a habit")

if st.button("Add Habit"):
    if habit:
        habits.append(habit)
        with open(habit_file, "w") as f:
            json.dump(habits, f)
        st.success(f"{habit} added successfully! ✅")
    else:
        st.error("Please enter a habit!")

st.write("**Your habits:**")
for h in habits:
    st.write("-", h)

# ----------------- AI Chatbot -----------------
st.subheader("🤖 AI Chatbot")
chat_file = "chat_history.json"

# Load chat history
if os.path.exists(chat_file):
    with open(chat_file, "r") as f:
        chat_history = json.load(f)
else:
    chat_history = []

user_input = st.text_input("Ask something...")

if st.button("Ask AI"):
    if user_input:
        # Check for special question about creator
        if "who created you" in user_input.lower():
            answer = "Sri Varshini Nagulapati 💖"
        else:
            try:
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

st.write(answer)



        # Save chat
        chat_history.append({"question": user_input, "answer": answer})
        with open(chat_file, "w") as f:
            json.dump(chat_history, f)

# Display chat history
st.write("**Chat History:**")
for chat in chat_history:
    st.write("You:", chat["question"])
    st.write("AI:", chat["answer"])

# Delete chat option
if st.button("Delete Chat History"):
    chat_history = []
    with open(chat_file, "w") as f:
        json.dump(chat_history, f)
    st.success("Chat history cleared ✅")
