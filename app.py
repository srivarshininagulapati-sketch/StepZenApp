import streamlit as st
import google.generativeai as genai

# -----------------------------
# Configure your Google API key
# -----------------------------
# Make sure you have your API key in .streamlit/secrets.toml as:
# GOOGLE_API_KEY="YOUR_API_KEY_HERE"
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# -----------------------------
# Welcome Section
# -----------------------------
st.title("Hello Varshini 💖")
st.write("Welcome to StepZen 🌍 - My first Streamlit app 🚀")

# -----------------------------
# Habit Tracker Section
# -----------------------------
st.subheader("StepZen Habit Tracker 🌟")
st.write("Track your daily habits easily!")

habit = st.text_input("Enter a habit")
if st.button("Add Habit"):
    if habit:
        st.success(f"{habit} added to your habits! ✅")
    else:
        st.error("Please enter a habit!")

# -----------------------------
# AI Chatbot Section
# -----------------------------
st.subheader("StepZen AI Chatbot 🤖")
user_input = st.text_input("You:", key="chat_input")

if st.button("Send AI Response"):
    if user_input:
        try:
            response = genai.models.generate_content(
                model="models/gemini-2.5-flash",
                prompt=user_input
            )
            # Display AI response
            st.text_area("AI:", value=response.content[0].text, height=150)
        except Exception as e:
            st.error(f"Error generating AI response: {e}")
