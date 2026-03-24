import streamlit as st
import datetime
from supabase import create_client
import google.generativeai as genai
from gtts import gTTS

st.set_page_config(page_title="ZenChat AI", layout="wide")

# ---------------- SECRETS ----------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

# ---------------- INIT ----------------
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# ---------------- AI PERSONALITY ----------------
SYSTEM_PROMPT = """
You are ZenChat AI 💚
- Friendly
- Smart
- Helpful
- Motivational
- Talk like a human
"""

# ---------------- LOGIN ----------------
st.sidebar.title("🔐 Login")
email = st.sidebar.text_input("Enter Email")

if not email:
    st.stop()

# ---------------- USER ----------------
user_data = supabase.table("users").select("*").eq("email", email).execute()

if user_data.data:
    user = user_data.data[0]
else:
    user = {
        "email": email,
        "plan": "Free",
        "habits": []
    }
    supabase.table("users").insert(user).execute()

# ---------------- SIDEBAR ----------------
st.sidebar.subheader("💬 Chats")

sessions = supabase.table("chat_sessions").select("*").eq("user_id", email).execute()

if st.sidebar.button("➕ New Chat"):
    supabase.table("chat_sessions").insert({
        "user_id": email,
        "title": "New Chat"
    }).execute()
    st.rerun()

selected_session = None

for s in sessions.data:
    col1, col2 = st.sidebar.columns([3,1])
    if col1.button(s["title"], key=s["id"]):
        selected_session = s["id"]
    if col2.button("❌", key=f"del_s_{s['id']}"):
        supabase.table("chat_sessions").delete().eq("id", s["id"]).execute()
        st.rerun()

# ---------------- UI ----------------
st.title("🤖 ZenChat AI")
st.markdown("Created by **Srivarshini 💖**")

# ---------------- HABITS ----------------
st.subheader("📅 Habit Tracker")

new_habit = st.text_input("Add Habit")

if st.button("Add Habit") and new_habit:
    user["habits"].append(new_habit)
    supabase.table("users").update({"habits": user["habits"]}).eq("email", email).execute()
    st.rerun()

for i, h in enumerate(user["habits"]):
    col1, col2 = st.columns([4,1])
    col1.write(f"✔️ {h}")
    if col2.button("❌", key=f"h_{i}"):
        user["habits"].pop(i)
        supabase.table("users").update({"habits": user["habits"]}).eq("email", email).execute()
        st.rerun()

# ---------------- CHAT ----------------
st.subheader("💬 Chat")

if selected_session:

    messages = supabase.table("messages").select("*").eq("session_id", selected_session).execute()

    for m in messages.data:
        with st.chat_message(m["role"]):
            st.write(m["content"])

            if st.button("❌", key=f"msg_{m['id']}"):
                supabase.table("messages").delete().eq("id", m["id"]).execute()
                st.rerun()

    prompt = st.chat_input("Type message...")

    if prompt:
        supabase.table("messages").insert({
            "session_id": selected_session,
            "role": "user",
            "content": prompt
        }).execute()

        full_prompt = SYSTEM_PROMPT + "\nUser: " + prompt

        res = model.generate_content(full_prompt)
        ans = res.text

        supabase.table("messages").insert({
            "session_id": selected_session,
            "role": "assistant",
            "content": ans
        }).execute()

        # Voice
        tts = gTTS(ans)
        tts.save("voice.mp3")
        audio = open("voice.mp3", "rb").read()
        st.audio(audio)

        st.rerun()

# ---------------- IMAGE AI ----------------
st.subheader("🖼️ Image AI")

img = st.file_uploader("Upload Image")

if img:
    st.image(img)

    if st.button("Analyze Image"):
        response = model.generate_content([
            "Explain this image",
            img.getvalue()
        ])
        st.write(response.text)

# ---------------- PLAN ----------------
st.subheader("💳 Upgrade Plan")

import razorpay

# Razorpay client initialize
client = razorpay.Client(auth=(st.secrets["RAZORPAY_KEY_ID"], st.secrets["RAZORPAY_KEY_SECRET"]))

# Plan IDs mapping (already మీ దగ్గర ఉన్న Plan IDs)
PLAN_IDS = {
    "Silver": "plan_H1Xyz12345",  # మీ Razorpay Plan ID
    "Gold": "plan_H1Xyz67890"
}

# User select box
plan = st.selectbox("Choose Plan", ["Free", "Silver", "Gold"])

# Upgrade Plan click
if st.button("Upgrade Plan"):
    if plan == "Free":
        # Free plan select అయినా Supabase update
        supabase.table("users").update({"plan": "Free"}).eq("email", email).execute()
        st.success("Plan updated to Free")
    else:
        try:
            # Razorpay subscription create
            subscription = client.subscription.create({
                "plan_id": PLAN_IDS[plan],
                "customer_notify": 1,
                "total_count": 12  # 12 months subscription
            })

            # Razorpay Checkout button show చేయడం
            st.markdown(f"""
            <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
            <button id="rzp-button">Pay Now</button>
            <script>
            var options = {{
                "key": "{st.secrets['RAZORPAY_KEY_ID']}",
                "subscription_id": "{subscription['id']}",
                "handler": function (response) {{
                    alert('Payment successful! Your plan is now active.');
                    window.location.reload();
                }}
            }};
            var rzp = new Razorpay(options);
            document.getElementById('rzp-button').onclick = function(e){{
                rzp.open();
                e.preventDefault();
            }}
            </script>
            """, unsafe_allow_html=True)

            st.info("Click 'Pay Now' to complete your subscription payment.")

        except Exception as e:
            st.error(f"Payment error: {e}")
# ---------------- ADMIN ----------------
st.subheader("📊 Admin Dashboard")

users = supabase.table("users").select("*").execute().data

total_users = len(users)
paid_users = len([u for u in users if u["plan"] != "Free"])

st.metric("👥 Users", total_users)
st.metric("💎 Paid Users", paid_users)