import streamlit as st
import json
import os
import pandas as pd
from google import genai

# -------------------------------
# 1️⃣ User Email Login
# -------------------------------
st.title("Hello Varshini 💖")
st.write("Welcome to your Habit Tracker & AI Chatbot App 🚀")

if "user_email" not in st.session_state:
    st.session_state.user_email = st.text_input("Enter your email to start:")

if st.session_state.user_email:
    user_email = st.session_state.user_email
    st.success(f"Welcome, {user_email}!")

    # -------------------------------
    # 2️⃣ File Paths for this user
    # -------------------------------
    habits_file = f"habits_{user_email}.json"
    chat_file = f"chat_{user_email}.json"

    # Initialize files if not exist
    if not os.path.exists(habits_file):
        with open(habits_file, "w") as f:
            json.dump([], f)
    if not os.path.exists(chat_file):
        with open(chat_file, "w") as f:
            json.dump([], f)

    # Load data
    with open(habits_file, "r") as f:
        st.session_state.habits = json.load(f)
    with open(chat_file, "r") as f:
        st.session_state.chat_history = json.load(f)

    # -------------------------------
    # 3️⃣ Configure Gemini API
    # -------------------------------
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

    # -------------------------------
    # 4️⃣ Layout: Columns for Styling
    # -------------------------------
    col1, col2 = st.columns(2)

    # -------------------------------
    # 4a️⃣ Habit Tracker
    # -------------------------------
    with col1:
        st.subheader("🌟 Habit Tracker")
        habit = st.text_input("Enter a habit")
        if st.button("Add Habit"):
            if habit:
                st.session_state.habits.append(habit)
                with open(habits_file, "w") as f:
                    json.dump(st.session_state.habits, f)
                st.success(f"{habit} added successfully! ✅")
            else:
                st.error("Please enter a habit!")

        # Show habits + delete option
        if st.session_state.habits:
            st.write("Your habits:")
            to_delete = st.multiselect("Select habits to delete:", st.session_state.habits)
            if st.button("Delete Selected Habits") and to_delete:
                for h in to_delete:
                    st.session_state.habits.remove(h)
                with open(habits_file, "w") as f:
                    json.dump(st.session_state.habits, f)
                st.success("Selected habits deleted ✅")
            for h in st.session_state.habits:
                st.write(f"- {h}")

        # Download habits
        if st.session_state.habits:
            st.download_button(
                label="Download Habits",
                data=json.dumps(st.session_state.habits),
                file_name=f"habits_{user_email}.json",
                mime="application/json"
            )

    # -------------------------------
    # 4b️⃣ AI Chatbot
    # -------------------------------
    with col2:
        st.subheader("🤖 AI Chatbot")
        user_input = st.text_input("Ask something...")
        if st.button("Ask AI") and user_input:
            # Check if question already exists
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
                        contents=user_input,
                    )
                    answer = response.text
                    st.session_state.chat_history.append({"question": user_input, "answer": answer})
                    with open(chat_file, "w") as f:
                        json.dump(st.session_state.chat_history, f)
                    st.write(answer)
                except Exception as e:
                    st.warning("API quota reached or error occurred. Please try again later.")

        # Show chat history + delete option
        if st.session_state.chat_history:
            st.subheader("💬 Chat History")
            to_delete_chat = []
            for i, c in enumerate(st.session_state.chat_history):
                if st.checkbox(f"Delete Q: {c['question']}", key=f"del{i}"):
                    to_delete_chat.append(c)
            if st.button("Delete Selected Chat Messages") and to_delete_chat:
                for c in to_delete_chat:
                    st.session_state.chat_history.remove(c)
                with open(chat_file, "w") as f:
                    json.dump(st.session_state.chat_history, f)
                st.success("Selected chat messages deleted ✅")

            # Display chat history
            for c in st.session_state.chat_history:
                st.markdown(f"**Q:** {c['question']}\n**A:** {c['answer']}")

            # Download chat history as CSV
            df = pd.DataFrame(st.session_state.chat_history)
            st.download_button(
                label="Download Chat History",
                data=df.to_csv(index=False),
                file_name=f"chat_{user_email}.csv",
                mime="text/csv"
            )

    # -------------------------------
    # 5️⃣ Creator Info
    # -------------------------------
    st.markdown("---")
    st.markdown("Created by Sri Varshini Nagulapati 💖")
