import streamlit as st
from google import genai

# Configure API key
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

st.title("Hello Varshini 💖")
st.write("My first Streamlit app 🚀")

st.subheader("🌟 Habit Tracker")

habit = st.text_input("Enter a habit")

if st.button("Add Habit"):
    if habit:
        st.success(f"{habit} added successfully! ✅")
    else:
        st.error("Please enter a habit!")

st.subheader("🤖 AI Chatbot")

user_input = st.text_input("Ask something...")

if st.button("Ask AI"):
    if user_input:
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_input,
            )
            st.write(response.text)
        except Exception as e:
            st.error(f"Error: {e}")
