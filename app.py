import streamlit as st
import datetime
import razorpay
import json
import os
from dotenv import load_dotenv

# ==============================
# LOAD ENV VARIABLES
# ==============================
load_dotenv()

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="AI Habit Tracker")
st.title("🤖 Chatbot")
st.caption("Created by Srivarshini Nagulapati")

# ==============================
# 🔴 ADD YOUR REAL PLAN IDs HERE
# ==============================
BASIC_PLAN_ID = "plan_SFBT9KT6xXg8Ua"
SILVER_PLAN_ID = "plan_SFBUBSaO3jLhGL"
GOLD_PLAN_ID = "plan_SFBVQIj73B3joe"

PLAN_LIMITS = {
    "Free": 20,
    "Basic": 50,
    "Silver": 100,
    "Gold": 400
}

DATA_FILE = "users.json"

# ==============================
# DATABASE SETUP
# ==============================
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

def load_users():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_users(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# ==============================
# LOGIN
# ==============================
email = st.text_input("Enter your Email")

if not email:
    st.stop()

users = load_users()

if email not in users:
    users[email] = {
        "plan": "Free",
        "chats_today": 0,
        "last_date": str(datetime.date.today()),
        "habits": [],
        "chat_history": []
    }
    save_users(users)

user = users[email]

# Reset daily usage
today = str(datetime.date.today())
if user["last_date"] != today:
    user["chats_today"] = 0
    user["last_date"] = today
    save_users(users)

st.write("### Current Plan:", user["plan"])
st.write("Chats Used Today:", user["chats_today"], "/", PLAN_LIMITS[user["plan"]])

# ==============================
# CHAT SECTION
# ==============================
st.subheader("🤖 AI Chat")

question = st.text_input("Ask something")

if st.button("Send"):
    if user["chats_today"] >= PLAN_LIMITS[user["plan"]]:
        st.error("Daily limit reached. Please upgrade.")
    else:
        answer = "AI Response to: " + question

        user["chat_history"].append({
            "q": question,
            "a": answer
        })

        user["chats_today"] += 1
        save_users(users)

        st.success(answer)

# ==============================
# CHAT HISTORY + DELETE
# ==============================
st.subheader("📝 Chat History")

if user["chat_history"]:
    for i, chat in enumerate(user["chat_history"]):
        st.write("Q:", chat["q"])
        st.write("A:", chat["a"])

        if st.button(f"Delete Chat {i}"):
            user["chat_history"].pop(i)
            save_users(users)
            st.rerun()

# Download
if user["chat_history"]:
    st.download_button(
        label="Download Chat History",
        data=json.dumps(user["chat_history"]),
        file_name="chat_history.json"
    )

# ==============================
# HABIT TRACKER
# ==============================
st.subheader("📅 Habit Tracker")

new_habit = st.text_input("Add New Habit")

if st.button("Add Habit"):
    if new_habit:
        user["habits"].append(new_habit)
        save_users(users)
        st.success("Habit Added!")

if user["habits"]:
    for habit in user["habits"]:
        st.write("✔️", habit)

# ==============================
# SUBSCRIPTION SECTION
# ==============================
st.subheader("💎 Upgrade Plan")

plan_choice = st.selectbox("Choose Plan", [
    "Basic - ₹99",
    "Silver - ₹199",
    "Gold - ₹499"
])

if st.button("Subscribe"):
    try:
        if plan_choice == "Basic - ₹99":
            selected_plan = BASIC_PLAN_ID
        elif plan_choice == "Silver - ₹199":
            selected_plan = SILVER_PLAN_ID
        else:
            selected_plan = GOLD_PLAN_ID

        subscription = client.subscription.create({
            "plan_id": selected_plan,
            "customer_notify": 1,
            "total_count": 12
        })

        st.success("Subscription Created Successfully!")
        st.write("Subscription ID:", subscription["id"])

    except Exception as e:
        st.error("Subscription Failed")
        st.write(e)
