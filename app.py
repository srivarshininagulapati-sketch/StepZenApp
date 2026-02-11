import streamlit as st
import google.generativeai as genai

# Configure your Google API key from Streamlit secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- Welcome Message ---
st.title("Hello Varshini 💖")
st.write("My first Streamlit app 🚀")

# --- Habit Tracker ---
st.header("StepZen Habit Tracker 🌟")
st.write("Welcome! Track your daily habits easily.")

habit = st.text_input("Enter a habit")
if st.button("Add Habit"):
    if habit:
        st.success(f"{habit} added to your habits! ✅")
    else:
        st.error("Please enter a habit!")

# --- AI Chatbot ---
st.header("StepZen AI Chatbot 🤖")
user_input = st.text_input("You: ", key="chat_input")

if st.button("Send", key="chat_button"):
    if user_input:
        try:
            response = genai.chat.create(
                model="models/gemini-3-pro-preview",  # Use a valid model from your list
                messages=[{"role": "user", "content": user_input}],
            )
            bot_reply = response.output_text
            st.text_area("Bot:", value=bot_reply, height=150)
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.error("Please type a message to chat!")
