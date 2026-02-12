import os
import json
import datetime
import streamlit as st
from dotenv import load_dotenv
import razorpay

# -------------------------------
# Load API keys
# -------------------------------
load_dotenv()  # Loads Razorpay keys from root .env
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

# Google API key from Streamlit secrets
GOOGLE_API_KEY = st.secrets.get("google_api_key")

# Safety warnings
if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
    st.warning("⚠ Razorpay keys missing in your .env!")
if not GOOGLE_API_KEY:
    st.warning("⚠ Google API key missing in Streamlit secrets!")

# Initialize Razorpay client only if keys exist
if RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET:
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
    "Silver": {"chats_per_day": 100, "price": 199, "plan_id": "plan_silver"},  # Replace with actual Razorpay plan_id
    "Gold": {"chats_per_day": 400, "price": 399, "plan_id": "plan_gold"}       # Replace with actual Razorpay plan_id
}

# -------------------------------
# User Login
# -------------------------------
email = st.text_input("Enter your Email")
if email:
    with open(USERS_FILE, "r") as f:
        users = json.load(f)

    # If new user, initialize
    if email not in users:
        users[email] = {
            "plan": "Free",
            "habits": [],
            "chats": [],
            "chats_used_today": 0,
            "last_chat_date": str(datetime.date.today())
        }

    user = users[email]

    # -------------------------------
    # Reset daily chat count if date changed
    # -------------------------------
    user.setdefault("last_chat_date", "")
    user.setdefault("chats_used_today", 0)
    user.setdefault("chats", [])
    today_str = str(datetime.date.today())
    if user["last_chat_date"] != today_str:
        user["last_chat_date"] = today_str
        user["chats_used_today"] = 0

    st.markdown(f"**Current Plan:** {user['plan']}")
    st.markdown(f"**Chats Used Today:** {user['chats_used_today']} / {PLANS[user['plan']]['chats_per_day']}")

    # -------------------------------
    # Habit Tracker
    # -------------------------------
    st.subheader("📅 Habit Tracker")
    new_habit = st.text_input("Add New Habit")
    if new_habit:
        user["habits"].append(new_habit)
        users[email] = user
        with open(USERS_FILE, "w") as f:
            json.dump(users, f)

    for idx, h in enumerate(user["habits"]):
        st.write(f"✔️ {h}")
        if st.button(f"Delete {h}", key=f"del_habit{idx}"):
            user["habits"].pop(idx)
            users[email] = user
            with open(USERS_FILE, "w") as f:
                json.dump(users, f)
            st.stop()  # stops and reruns safely

    # -------------------------------
    # AI Chat
    # -------------------------------
    st.subheader("🤖 AI Chat")
    question = st.text_input("Ask something...", key="chat_input")
    if question:
        if user["chats_used_today"] >= PLANS[user['plan']]['chats_per_day']:
            st.error("You reached your daily chat limit. Upgrade plan for more.")
        else:
            try:
                from google_genai import Client
                gen_client = Client(api_key=GOOGLE_API_KEY)
                response = gen_client.generate_text(prompt=question)
                user["chats"].append({"Q": question, "A": response})
                user["chats_used_today"] += 1
                users[email] = user
                with open(USERS_FILE, "w") as f:
                    json.dump(users, f)
                st.success(f"A: {response}")
            except Exception as e:
                st.error(f"AI bot error: {str(e)}")

    # -------------------------------
    # Display chat history
    # -------------------------------
    st.subheader("💬 Chat History")
    for idx, c in enumerate(user["chats"]):
        st.write(f"Q: {c['Q']}")
        st.write(f"A: {c['A']}")
        if st.button(f"Delete Chat {idx}", key=f"del_chat{idx}"):
            user["chats"].pop(idx)
            users[email] = user
            with open(USERS_FILE, "w") as f:
                json.dump(users, f)
            st.stop()  # safe rerun

    # -------------------------------
    # Upgrade Plan
    # -------------------------------
    st.subheader("💎 Upgrade Plan")
    selected_plan = st.selectbox("Choose Plan", list(PLANS.keys()))
    if selected_plan != user['plan']:
        if PLANS[selected_plan]['price'] == 0:
            user['plan'] = selected_plan
            users[email] = user
            with open(USERS_FILE, "w") as f:
                json.dump(users, f)
            st.success("Plan changed to Free")
        else:
            if RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET:
                if st.button(f"Subscribe to {selected_plan} - ₹{PLANS[selected_plan]['price']}"):
                    try:
                        subscription = rz_client.subscription.create({
                            "plan_id": PLANS[selected_plan]["plan_id"],
                            "customer_notify": 1,
                            "total_count": 12
                        })
                        user['plan'] = selected_plan
                        users[email] = user
                        with open(USERS_FILE, "w") as f:
                            json.dump(users, f)
                        st.success(f"Subscribed to {selected_plan}!")
                    except Exception as e:
                        st.error(f"Subscription Failed: {str(e)}")
            else:
                st.warning("⚠ Razorpay keys missing. Cannot subscribe!")

    # Save user updates at the end
    users[email] = user
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)