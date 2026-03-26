import streamlit as st
import datetime
import requests
import json
import google.generativeai as genai
from gtts import gTTS

# ---------------- Optional Razorpay import ----------------
try:
    import razorpay
except ModuleNotFoundError:
    razorpay = None
    st.warning("Razorpay module not installed. Payment features disabled.")

# ---------------- Page config ----------------
st.set_page_config(page_title="ZenChat AI", layout="wide")

# ---------------- Secrets ----------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]  # REST endpoint
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

# ---------------- Init REST API functions ----------------
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def supabase_get(table, filter_col=None, filter_val=None):
    url = f"{SUPABASE_URL}/{table}"
    if filter_col and filter_val:
        url += f"?{filter_col}=eq.{filter_val}"
    r = requests.get(url, headers=headers)
    return r.json() if r.status_code == 200 else []

def supabase_insert(table, data):
    url = f"{SUPABASE_URL}/{table}"
    r = requests.post(url, headers=headers, json=data)
    return r.json() if r.status_code in [200, 201] else []

def supabase_update(table, data, filter_col, filter_val):
    url = f"{SUPABASE_URL}/{table}?{filter_col}=eq.{filter_val}"
    r = requests.patch(url, headers=headers, json=data)
    return r.json() if r.status_code == 200 else []

def supabase_delete(table, filter_col, filter_val):
    url = f"{SUPABASE_URL}/{table}?{filter_col}=eq.{filter_val}"
    r = requests.delete(url, headers=headers)
    return r.status_code

# ---------------- Google AI init ----------------
genai.configure(api_key=GOOGLE_API_KEY)

# Step 1: List all available models (temporary)
models = genai.list_models()
st.write("Available models:", models)

# For now, comment out the old model line
# model = genai.GenerativeModel("gemini-1.5-flash") # ---------------- AI Personality ----------------
SYSTEM_PROMPT = """
You are ZenChat AI 💚
- Friendly
- Smart
- Helpful
- Motivational
- Talk like a human
"""

# ---------------- Login ----------------
st.sidebar.title("🔐 Login")
email = st.sidebar.text_input("Enter Email")
if not email:
    st.stop()

# ---------------- User ----------------
user_data = supabase_get("users", "email", email)
if user_data:
    user = user_data[0]
else:
    user = {"email": email, "plan": "Free", "habits": []}
    supabase_insert("users", user)

# ---------------- Sidebar - Chats ----------------
st.sidebar.subheader("💬 Chats")
sessions = supabase_get("chat_sessions", "user_id", email)

if st.sidebar.button("➕ New Chat"):
    supabase_insert("chat_sessions", {"user_id": email, "title": "New Chat"})
    st.experimental_rerun()

selected_session = None
for s in sessions:
    col1, col2 = st.sidebar.columns([3,1])
    if col1.button(s["title"], key=s["title"]):
        selected_session = s.get("id")
    if col2.button("❌", key=f"del_s_{s['title']}"):
        supabase_delete("chat_sessions", "id", s.get("id"))
        st.experimental_rerun()

# ---------------- Ensure session exists ----------------
if not selected_session:
    new_session = supabase_insert({"user_id": email, "title": "New Chat"}, "chat_sessions")
    selected_session = new_session[0]["id"] if new_session else None

# ---------------- UI ----------------
st.title("🤖 ZenChat AI")
st.markdown("Created by **Srivarshini 💖**")

# ---------------- Habit Tracker ----------------
st.subheader("📅 Habit Tracker")
new_habit = st.text_input("Add Habit")
if st.button("Add Habit") and new_habit:
    user["habits"].append(new_habit)
    supabase_update("users", {"habits": user["habits"]}, "email", email)
    st.experimental_rerun()

for i, h in enumerate(user["habits"]):
    col1, col2 = st.columns([4,1])
    col1.write(f"✔️ {h}")
    if col2.button("❌", key=f"h_{i}"):
        user["habits"].pop(i)
        supabase_update("users", {"habits": user["habits"]}, "email", email)
        st.experimental_rerun()

# ---------------- Chat ----------------
st.subheader("💬 Chat")
messages = supabase_get("messages", "session_id", selected_session)

for m in messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])
        if st.button("❌", key=f"msg_{m['id']}"):
            supabase_delete("messages", "id", m["id"])
            st.experimental_rerun()

prompt = st.chat_input("Type message...")
if prompt:
    supabase_insert("messages", {"session_id": selected_session, "role": "user", "content": prompt})
    full_prompt = SYSTEM_PROMPT + "\nUser: " + prompt
    res = model.generate_content(full_prompt)
    ans = res.text
    supabase_insert("messages", {"session_id": selected_session, "role": "assistant", "content": ans})

    tts = gTTS(ans)
    tts.save("voice.mp3")
    st.audio("voice.mp3")

    st.experimental_rerun()

# ---------------- Image AI ----------------
st.subheader("🖼️ Image AI")
img = st.file_uploader("Upload Image")
if img:
    st.image(img)
    if st.button("Analyze Image"):
        response = model.generate_content([ "Explain this image", img.getvalue() ])
        st.write(response.text)

# ---------------- Plan System ----------------
st.subheader("💳 Upgrade Plan")
plan = st.selectbox("Choose Plan", ["Free", "Silver", "Gold"])
if st.button("Upgrade Plan"):
    supabase_update("users", {"plan": plan}, "email", email)
    st.success(f"Plan updated to {plan}")

    if razorpay and plan != "Free":
        PLAN_IDS = {"Silver":"plan_SFBUBSaO3jLhGL","Gold":"plan_SFBVQIj73B3joe"}
        client = razorpay.Client(auth=(st.secrets["RAZORPAY_KEY_ID"], st.secrets["RAZORPAY_KEY_SECRET"]))
        try:
            subscription = client.subscription.create({"plan_id": PLAN_IDS[plan],"customer_notify":1,"total_count":12})
            st.info(f"Razorpay subscription created. ID: {subscription['id']}")
        except Exception as e:
            st.error(f"Payment error: {e}")

# ---------------- Admin Dashboard ----------------
st.subheader("📊 Admin Dashboard")
users = supabase_get("users")
total_users = len(users)
paid_users = len([u for u in users if u.get("plan") != "Free"])
st.metric("👥 Users", total_users)
st.metric("💎 Paid Users", paid_users)