import streamlit as st
import json
import datetime
import os
from dotenv import load_dotenv

# ----------------------------
# ENV & SECRETS
# ----------------------------

load_dotenv()  # Only for local development

RAZORPAY_KEY_ID = os.environ.get("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.environ.get("RAZORPAY_KEY_SECRET")

if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
    st.warning("⚠ Razorpay keys missing!")

try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    GOOGLE_API_KEY = None
    st.warning("⚠ Google API key missing in Streamlit secrets!")

# ----------------------------
# GOOGLE GENAI IMPORT (CORRECT)
# ----------------------------

try:
    from google import genai
except ImportError:
    genai = None
    st.error("Google GenAI module not installed. Check requirements.txt")

client = None
if genai and GOOGLE_API_KEY:
    client = genai.Client(api_key=GOOGLE_API_KEY)

# ----------------------------
# USERS STORAGE
# ----------------------------

USERS_FILE = "users.json"

if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
else:
    users = {}

def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

# ----------------------------
# PLANS
# ----------------------------

PLANS = {
    "Free": {"daily_limit": 20, "price": 0},
    "Silver": {"daily_limit": 100, "price": 199},
    "Gold": {"daily_limit": 400, "price": 399},
}

# ----------------------------
# UI
# ----------------------------

st.title("Chatbot & Habit Tracker")
st.markdown("Created by **Srivarshini Nagulapati 💖**")

email = st.text_input("Enter your Email")

if not email:
    st.stop()

# ----------------------------
# USER INITIALIZATION
# ----------------------------

today = str(datetime.date.today())

if email not in users:
    users[email] = {
        "email": email,
        "plan": "Free",
        "chats_today": 0,
        "last_chat_date": today,
        "habits": [],
        "chats": []
    }

user = users[email]

# Reset daily chats if new day
if user["last_chat_date"] != today:
    user["chats_today"] = 0
    user["last_chat_date"] = today

save_users()

# ----------------------------
# USER INFO
# ----------------------------

st.write(f"Current Plan: {user['plan']}")
st.write(f"Chats Used Today: {user['chats_today']} / {PLANS[user['plan']]['daily_limit']}")

# ----------------------------
# HABIT TRACKER
# ----------------------------

st.subheader("📅 Habit Tracker")

new_habit = st.text_input("Add New Habit")

if st.button("Add Habit") and new_habit:
    user["habits"].append(new_habit)
    save_users()

for h in user["habits"]:
    st.write(f"✔️ {h}")

# ----------------------------
# AI CHAT
# ----------------------------

st.subheader("🤖 AI Chat")

question = st.text_input("Ask something")

if st.button("Send") and question:

    if user["chats_today"] >= PLANS[user['plan']]['daily_limit']:
        st.error("Daily chat limit reached. Upgrade plan for more chats!")
    else:
        response_text = "AI unavailable."

        if client:
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=question
                )
                response_text = response.text
            except Exception as e:
                response_text = f"Error: {str(e)}"

        user["chats"].append({"Q": question, "A": response_text})
        user["chats_today"] += 1
        save_users()

        st.write("AI Response:")
        st.write(response_text)

# ----------------------------
# CHAT HISTORY
# ----------------------------

st.subheader("💬 Chat History")

for c in user["chats"]:
    st.markdown(f"**Q:** {c['Q']}")
    st.markdown(f"**A:** {c['A']}")
    st.markdown("---")

# ----------------------------
# UPGRADE PLAN
# ----------------------------

st.subheader("💎 Upgrade Plan")

selected_plan = st.radio("Choose Plan", options=["Free", "Silver", "Gold"])
plan_info = PLANS[selected_plan]

st.write(f"Daily Chat Limit: {plan_info['daily_limit']}")
st.write(f"Price per month: ₹{plan_info['price']}")

if plan_info["price"] > 0:

    if not (RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET):
        st.warning("⚠ Razorpay keys missing. Cannot subscribe!")
    else:
        import razorpay
        razor_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

        if st.button(f"Subscribe to {selected_plan} Plan"):
            try:
                user["plan"] = selected_plan
                save_users()
                st.success(f"Subscription activated: {selected_plan}")
            except Exception as e:
                st.error(f"Subscription Failed: {str(e)}")

# ----------------------------
# EXPORT
# ----------------------------

st.subheader("💾 Export Data")

if st.button("Download JSON"):
    st.download_button(
        label="Download",
        data=json.dumps(user, indent=4),
        file_name="user_data.json",
        mime="application/json"
    )
