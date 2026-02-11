import streamlit as st
from google.genai import Client

# Initialize client with secret key
client = Client(api_key=st.secrets["GOOGLE_API_KEY"])

st.title("My First Chatbot App")

# Example question
user_question = st.text_input("Ask a question:")

if user_question:
    response = client.chat(
        model="chat-bison-001",
        messages=[{"role": "user", "content": user_question}]
    )
    answer = response.last.message.content
    st.write(answer)
