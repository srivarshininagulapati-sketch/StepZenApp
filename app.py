import streamlit as st
import os
import json
from google import genai

# =====================
# Gemini API Client
# =====================
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

# =====================
# User Login
# =====================
if "user_email" not in st.session_state:
    st.session_state.user_email = st.text_input("Enter your email to start:")

if st.session_state.user_email:
    user_email = st.session_state.user_email
    st.success(f"Welcome, {user_email}!")

    # =====================
    # File paths per user
    # =====================
    habits_file = f"habits_{user_email}.json"
    chat_file = f"chat_{user_email}.json"

    # =====================
    # Load habits & chat history
    # =====================
    if os.path.exists(habits_file):
        with open(habits_file, "r") as f:
            st.session_state.habits = json.load(f)
    else:
        st.session_state.habits = []

    if os.path.exists(chat_file):
        with open(chat_file, "r") as f:
            st.session_state.chat_history = json.load(f)
    else:
        st.session_state.chat_history = []

    # =====================
    # Habit Tracker
    # =====================
    st.subheader("🌟 Habit Tracker")
    habit = st.text_input("Enter a habit")

    if st.button("Add Habit"):
        if habit:
            st.session_state.habits.append(habit)
            # Save to JSON
            with open(habits_file, "w") as f:
                json.dump(st.session_state.habits, f)
            st.success(f"{habit} added successfully! ✅")
        else:
            st.error("Please enter a habit!")

    if st.session_state.habits:
        st.write("Your habits:")
        for h in st.session_state.habits:
            st.write(f"- {h}")

    # =====================
    # AI Chatbot
    # =====================
    st.subheader("🤖 AI Chatbot")
    user_input = st.text_input("Ask something...")

    if st.button("Ask AI") and user_input:
        if user_input.strip() == "":
            st.error("Please enter a question!")
        else:
            # Check if question was already asked
            existing = [c["question"] for c in st.session_state.chat_history]
            if user_input in existing:
                for c in st.session_state.chat_history:
                    if c["question"] == user_input:
                        st.info("Retrieved from history:")
                        st.write(c["answer"])
            else:
                try:
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=user_input
                    )
                    answer = response.text
                    st.write(answer)

                    # Save chat
                    st.session_state.chat_history.append({
                        "question": user_input,
                        "answer": answer
                    })
                    with open(chat_file, "w") as f:
                        json.dump(st.session_state.chat_history, f)
                except Exception as e:
                    st.error(f"Error: {e}")

    # =====================
    # Show previous chat history
    # =====================
    if st.session_state.chat_history:
        st.subheader("💬 Chat History")
        for c in st.session_state.chat_history:
            st.write(f"**Q:** {c['question']}")
            st.write(f"**A:** {c['answer']}")
            st.markdown("---")

    # =====================
    # Creator info
    # =====================
    st.markdown("Created by **Sri Varshini Nagulapati** 💖")
