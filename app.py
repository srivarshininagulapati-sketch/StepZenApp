import streamlit as st
import google.generativeai as genai

# Configure your API key
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# =========================
# Welcome Section
# =========================
st.title("Hello Varshini 💖")
st.write("My first Streamlit app 🚀")

# =========================
# Habit Tracker Section
# =========================
st.header("StepZen Habit Tracker 🌟")
habit = st.text_input("Enter a habit")
if st.button("Add Habit"):
    if habit:
        st.success(f"{habit} added to your habits! ✅")
    else:
        st.error("Please enter a habit!")

# =========================
# AI Chatbot Section
# =========================
st.header("StepZen AI Chatbot 🤖")
user_input = st.text_input("Ask me anything:")
if st.button("Send"):
    if user_input:
        try:
            # Use the new method generate_content
            response = genai.generate_content(
                model="models/gemini-2.5-flash",
                prompt=user_input
            )
            st.write("Chatbot:", response.text)
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Please type a question!")
