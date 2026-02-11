import streamlit as st
import json
from google.genai import Client  # latest package

# Load secrets
client = Client(api_key=st.secrets["GOOGLE_API_KEY"])

st.title("My First Chatbot App")

question = st.text_input("Ask a question:")

if st.button("Send"):
    if question:
        response = client.responses.create(
            model="models/text-bison-001",
            input=question
        )
        st.write(response.output_text)
