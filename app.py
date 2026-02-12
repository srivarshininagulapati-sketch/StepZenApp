import os
from dotenv import load_dotenv
import streamlit as st

# Load Razorpay keys from root .env
load_dotenv()
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

# Load Google API key from Streamlit secrets
GOOGLE_API_KEY = st.secrets.get("google_api_key")

# Safety check
if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
    st.warning("⚠ Razorpay keys missing in your .env!")
if not GOOGLE_API_KEY:
    st.warning("⚠ Google API key missing in Streamlit secrets!")

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
    "Free": {"chats_per_day": 20, "price": 0, "plan_SFBT9KT6xXg8Ua": None},
    "Silver": {"chats_per_day": 100, "price": 199, "plan_SFBUBSaO3jLhGL": "plan_silver"},
    "Gold": {"chats_per_day": 400, "price": 399, "plan_SFBVQIj73B3joe": "plan_gold"}
}

# -------------------------------
# User Login
# -------------------------------
email = st.text_input("Enter your Email")
if email:
    # Load users safely
    try:
        with open(USERS_FILE, "r") as f:
            users = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        users = {}

    # Initialize new user if not exist
    if email not in users:
        users[email] = {
            "plan": "Free",
            "habits": [],
            "chats": [],
            "chats_used_today": 0,
            "last_chat_date": str(datetime.date.today())
        }

    user = users[email]

    # Ensure all required keys exist (for old users)
    user.setdefault("habits", [])
    user.setdefault("chats", [])
    user.setdefault("chats_used_today", 0)
    user.setdefault("last_chat_date", str(datetime.date.today()))

    # Reset daily chat count if date changed
    today_str = str(datetime.date.today())
    if user["last_chat_date"] != today_str:
        user["last_chat_date"] = today_str
        user["chats_used_today"] = 0

    users[email] = user
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
        users[email] = user
        with open(USERS_FILE, "w") as f:
            json.dump(users, f)

    for idx, h in enumerate(user["habits"]):
        st.write(f"✔️ {h}")  # Display habit
        if st.button(f"Delete {h}", key=f"del_habit{idx}"):
            user["habits"].pop(idx)
            users[email] = user
            with open(USERS_FILE, "w") as f:
                json.dump(users, f)
            st.stop()  # Stops current run, updates UI

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

    # Display chat history
    st.subheader("💬 Chat History")
    for idx, c in enumerate(user["chats"]):
        st.write(f"Q: {c['Q']}")
        st.write(f"A: {c['A']}")
        if st.button(f"Delete Chat {idx}", key=f"del_chat{idx}"):
            user["chats"].pop(idx)
            users[email] = user
            with open(USERS_FILE, "w") as f:
                json.dump(users, f)
            st.stop()  # Stops current run, updates UI

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
