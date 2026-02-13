# app.py
import streamlit as st
import json
import datetime
import os
from dotenv import load_dotenv

# Load Razorpay keys from .env
load_dotenv()
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

# Check keys
if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
    st.warning("⚠ Razorpay keys missing in your .env!")

# Load Google API key from Streamlit secrets
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    GOOGLE_API_KEY = None
    st.warning("⚠ Google API key missing in Streamlit secrets!")

# Import Google GenAI client safely
try:
    from google_genai import Client as GenAIClient
except ModuleNotFoundError:
    GenAIClient = None
    st.warning("⚠ google_genai module missing. Install via pip!")

# Initialize Google AI client
client = None
if GenAIClient and GOOGLE_API_KEY:
    client = GenAIClient(api_key=GOOGLE_API_KEY)

# Users file
USERS_FILE = "users.json"
if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
else:
    users = {}

# Save users
def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

# Plans
PLANS = {
    "Free": {"daily_limit": 20, "price": 0},
    "Silver": {"daily_limit": 100, "price": 199},
    "Gold": {"daily_limit": 400, "price": 399},
}

# UI
st.title("Chatbot & Habit Tracker")
st.markdown("Created by **Srivarshini Nagulapati 💖**")

# Step 1: User email
email = st.text_input("Enter your Email")
if not email:
    st.stop()

# Initialize new user
if email not in users:
    users[email] = {
        "last_chat_date": str(datetime.date.today()),
        "chats_today": 0,
        "plan": "Free",
        "habits": [],
        "chats": []
    }
else:
    # Reset daily chats if new day
    if users[email].get("last_chat_date") != str(datetime.date.today()):
        users[email]["last_chat_date"] = str(datetime.date.today())
        users[email]["chats_today"] = 0

user = users[email]

# Show user info
st.write(f"Current Plan: {user['plan']}")
st.write(f"Chats Used Today: {user['chats_today']} / {PLANS[user['plan']]['daily_limit']}")

# Habit Tracker
st.subheader("📅 Habit Tracker")
new_habit = st.text_input("Add New Habit")
if st.button("Add Habit") and new_habit:
    user["habits"].append(new_habit)
    save_users()

for h in user["habits"]:
    st.write(f"✔️ {h}")

# AI Chat
st.subheader("🤖 AI Chat")
question = st.text_input("Ask something")

if st.button("Send") and question:
    if user["chats_today"] >= PLANS[user['plan']]['daily_limit']:
        st.error("Daily chat limit reached. Upgrade plan for more chats!")
    else:
        response_text = "API quota reached or AI client missing"
        if client:
            try:
                response = client.generate_content(
                    model="gemini-2.5-flash",
                    prompt=question,
                    max_output_tokens=200
                )
                response_text = response.output[0].content[0].text
            except Exception as e:
                response_text = f"Error: {str(e)}"
        user["chats"].append({"Q": question, "A": response_text})
        user["chats_today"] += 1
        save_users()
        st.write(f"AI Response to: {question}")
        st.write(response_text)

# Chat history
st.subheader("💬 Chat History")
for c in user["chats"]:
    st.markdown(f"**Q:** {c['Q']}\n\n**A:** {c['A']}")

# Upgrade Plans
st.subheader("💎 Upgrade Plan")
selected_plan = st.radio("Choose Plan", options=["Free", "Silver", "Gold"])
plan_info = PLANS[selected_plan]
st.write(f"Daily Chat Limit: {plan_info['daily_limit']}")
st.write(f"Price per month: ₹{plan_info['price']}")

# Razorpay subscription
if plan_info["price"] > 0:
    if not (RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET):
        st.warning("⚠ Razorpay keys missing. Cannot subscribe!")
    else:
        import razorpay
        client_razor = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        if st.button(f"Subscribe to {selected_plan} Plan"):
            try:
                # Simplified: real subscription requires Razorpay plan creation
                st.success(f"Subscription request for {selected_plan} sent! Complete payment in Razorpay dashboard.")
                user["plan"] = selected_plan
                save_users()
            except Exception as e:
                st.error(f"Subscription Failed: {str(e)}")

# Export
st.subheader("💾 Export Data")
if st.button("Download JSON"):
    with open("export.json", "w") as f:
        json.dump(user, f, indent=4)
    st.success("User data exported as export.json")
