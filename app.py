import streamlit as st
import datetime
from supabase import create_client
import google.generativeai as genai
import razorpay

# ----------------------------
# SECRETS (CLOUD SAFE)
# ----------------------------

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
RAZORPAY_KEY_ID = st.secrets["RAZORPAY_KEY_ID"]
RAZORPAY_KEY_SECRET = st.secrets["RAZORPAY_KEY_SECRET"]

# ----------------------------
# DATABASE CONNECTION
# ----------------------------

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ----------------------------
# GOOGLE AI SETUP
# ----------------------------

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# ----------------------------
# RAZORPAY CLIENT
# ----------------------------

rz_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# ----------------------------
# PLANS
# ----------------------------

PLANS = {
    "Free": {"daily_limit": 20, "price": 0, "plan_SFBT9KT6xXg8Ua": None},
    "Silver": {"daily_limit": 100, "price": 199, "plan_SFBUBSaO3jLhGL": "plan_ABC123XYZ"},  # replace with actual plan ID
    "Gold": {"daily_limit": 400, "price": 399, "plan_SFBVQIj73B3joe": "plan_DEF456XYZ"},    # replace with actual plan ID
}

# ----------------------------
# UI
# ----------------------------

st.title("Chatbot & Habit Tracker")
st.markdown("Created by **Srivarshini Nagulapati 💖**")

email = st.text_input("Enter your Email")
if not email:
    st.stop()

today = str(datetime.date.today())

# ----------------------------
# LOAD USER FROM SUPABASE
# ----------------------------

response = supabase.table("users").select("*").eq("email", email).execute()
if response.data:
    user = response.data[0]
else:
    user = {
        "email": email,
        "plan": "Free",
        "chats_today": 0,
        "last_chat_date": today,
        "habits": [],
        "chats": []
    }
    supabase.table("users").insert(user).execute()

# Reset daily chats
if user["last_chat_date"] != today:
    user["chats_today"] = 0
    user["last_chat_date"] = today
    supabase.table("users").update({
        "chats_today": 0,
        "last_chat_date": today
    }).eq("email", email).execute()

st.write(f"**Current Plan:** {user['plan']}")
st.write(f"**Chats Used Today:** {user['chats_today']} / {PLANS[user['plan']]['daily_limit']}")

# ----------------------------
# HABIT TRACKER
# ----------------------------

st.subheader("📅 Habit Tracker")

# Get new habit input from user
new_habit = st.text_input("Add New Habit")

# Add habit to user's data if the button is clicked
if st.button("Add Habit") and new_habit:
    user["habits"].append(new_habit)
    supabase.table("users").update({"habits": user["habits"]}).eq("email", email).execute()
    st.experimental_rerun()  # refresh app to show updated habits

# Display current habits
for h in user["habits"]:
    st.write(f"✔️ {h}")
