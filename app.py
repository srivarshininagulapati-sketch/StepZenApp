import streamlit as st
from google import genai

# Configure API key
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

st.title("Hello Varshini 💖")
st.write("My first Streamlit app 🚀")

# --- Habit Tracker ---
st.subheader("🌟 Habit Tracker")

# Initialize habits list in session
if "habits" not in st.session_state:
    st.session_state["habits"] = []

habit = st.text_input("Enter a habit")

if st.button("Add Habit"):
    if habit:
        st.session_state["habits"].append(habit)
        st.success(f"{habit} added successfully! ✅")
    else:
        st.error("Please enter a habit!")

if st.session_state["habits"]:
    st.write("**Your Habits:**")
    for h in st.session_state["habits"]:
        st.write("-", h)

# --- AI Chatbot ---
st.subheader("🤖 AI Chatbot")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

user_input = st.text_input("Ask something...")

if st.button("Ask AI"):
    if user_input:
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_input,
            )
            answer = response.text

            # Save question & answer in session
            st.session_state["chat_history"].append({"question": user_input, "answer": answer})

        except Exception as e:
            st.error(f"Error: {e}")

# Display chat history
if st.session_state["chat_history"]:
    st.write("**Chat History:**")
    for i, chat in enumerate(st.session_state["chat_history"], start=1):
        st.write(f"Q{i}: {chat['question']}")
        st.write(f"A{i}: {chat['answer']}")
