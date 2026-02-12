# app.py
import os
import json
import datetime
import streamlit as st
from dotenv import load_dotenv
import razorpay

# -------------------------------
# Load .env and secrets
# -------------------------------
load_dotenv()  # Loads .env from root folder

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

# Google Gemini API key from secrets/.env
with open("secrets/.env") as f:
    for line in f:
        if "GOOGLE_API_KEY" in line:
            GOOGLE_API_KEY = line.strip().split("=")[1]

# -------------------------------
# Razorpay Client
# -------------------------------
rz_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# -------------------------------
# Streamlit Setup
# -------------------------------
st.set_page_config(page_title="Habit Tracker & AI Chatbot", layout="wide")
st.title("Chatbot & Habit Tracker")
st.markdown("Created by **Srivarshini Nagulapati** 💖")

# -------------------------------
# Users Storage
# -------------------------------
USERS_FILE = "users.json"
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)

# -------------------------------
# Subscription Plans
# -------------------------------
PLANS = {
    "Free": {"chats_per_day": 20, "price": 0, "plan_id": None},
    "Silver": {"chats_per_day": 100, "price": 199, "plan_id": "plan_silver"},  # Replace with Razorpay plan_id
    "Gold": {"chats_per_day": 400, "price": 399, "plan_id": "plan_gold"}       # Replace with Razorpay plan_id
}

# -------------------------------
# User Login
# -------------------------------
email = st.text_input("Enter your Email")
if email:
    with open(USERS_FILE, "r") as f:
        users = json.load(f)

    if email not in users:
        users[email] = {
            "plan": "Free",
            "habits": [],
            "chats": [],
            "chats_used_today": 0,
            "last_chat_date": str(datetime.date.today())
        }
        with open(USERS_FILE, "w") as f:
            json.dump(users, f)

    user = users[email]

    # Reset daily chat count if date changed
    if user["last_chat_date"] != str(datetime.date.today()):
        user["chats_used_today"] = 0
        user["last_chat_date"] = str(datetime.date.today())
        with open(USERS_FILE, "w") as f:
            json.dump(users, f)

    st.markdown(f"**Current Plan:** {user['plan']}")
    st.markdown(f"**Chats Used Today:** {user['chats_used_today']} / {PLANS[user['plan']]['chats_per_day']}")

    # -------------------------------
    # Habit Tracker
    # -------------------------------
    st.subheader("📅 Habit Tracker")
    new_habit = st.text_input("Add New Habit")
    if new_habit:
        user["habits"].append(new_habit)
        with open(USERS_FILE, "w") as f:
            json.dump(users, f)

    for idx, h in enumerate(user["habits"]):
        st.write(f"✔️ {h}", key=f"habit{idx}")
        if st.button(f"Delete {h}", key=f"del_habit{idx}"):
            user["habits"].pop(idx)
            with open(USERS_FILE, "w") as f:
                json.dump(users, f)
            st.experimental_rerun()

    # -------------------------------
    # AI Chat
    # -------------------------------
    st.subheader("🤖 AI Chat")
    question = st.text_input("Ask something...")
    if question:
        if user["chats_used_today"] >= PLANS[user['plan']]['chats_per_day']:
            st.error("You reached your daily chat limit. Upgrade plan for more.")
        else:
            try:
                # Google GenAI Client
                from google_genai import Client
                gen_client = Client(api_key=GOOGLE_API_KEY)
                response = gen_client.generate_text(prompt=question)
                user["chats"].append({"Q": question, "A": response})
                user["chats_used_today"] += 1
                with open(USERS_FILE, "w") as f:
                    json.dump(users, f)
                st.success(f"A: {response}")
            except Exception as e:
                st.error(f"AI bot error: {str(e)}")

    # Display chat history
    st.subheader("💬 Chat History")
    for idx, c in enumerate(user["chats"]):
        st.write(f"Q: {c['Q']}")
        st.write(f"A: {c['A']}")
        if st.button(f"Delete Chat {idx}", key=f"del_chat{idx}"):
            user["chats"].pop(idx)
            with open(USERS_FILE, "w") as f:
                json.dump(users, f)
            st.experimental_rerun()

    # -------------------------------
    # Upgrade Plan
    # -------------------------------
    st.subheader("💎 Upgrade Plan")
    selected_plan = st.selectbox("Choose Plan", list(PLANS.keys()))
    if selected_plan != user['plan']:
        if PLANS[selected_plan]['price'] == 0:
            user['plan'] = selected_plan
            with open(USERS_FILE, "w") as f:
                json.dump(users, f)
            st.success("Plan changed to Free")
        else:
            if st.button(f"Subscribe to {selected_plan} - ₹{PLANS[selected_plan]['price']}"):
                try:
                    subscription = rz_client.subscription.create({
                        "plan_id": PLANS[selected_plan]["plan_id"],
                        "customer_notify": 1,
                        "total_count": 12
                    })
                    user['plan'] = selected_plan
                    with open(USERS_FILE, "w") as f:
                        json.dump(users, f)
                    st.success(f"Subscribed to {selected_plan}!")
                except Exception as e:
                    st.error(f"Subscription Failed: {str(e)}")
