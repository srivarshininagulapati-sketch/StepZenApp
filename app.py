import streamlit as st
import datetime
from supabase import create_client
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
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

# ---------------- Init ----------------
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# ---------------- AI Personality ----------------
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
user_data = supabase.table("users").select("*").eq("email", email).execute()

if user_data.data:
    user = user_data.data[0]
else:
    user = {"email": email, "plan": "Free", "habits": []}
    supabase.table("users").insert(user).execute()

# ---------------- Sidebar - Chats ----------------
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

# ---------------- Ensure session exists ----------------
if not selected_session:
    new_session = supabase.table("chat_sessions").insert({
        "user_id": email,
        "title": "New Chat"
    }).execute()
    selected_session = new_session.data[0]["id"]

# ---------------- UI ----------------
st.title("🤖 ZenChat AI")
st.markdown("Created by **Srivarshini 💖**")

# ---------------- Habit Tracker ----------------
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

# ---------------- Chat ----------------
st.subheader("💬 Chat")

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

    # Voice reply
    tts = gTTS(ans)
    tts.save("voice.mp3")
    st.audio("voice.mp3")

    st.rerun()

# ---------------- Image AI ----------------
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

# ---------------- Plan System ----------------
st.subheader("💳 Upgrade Plan")
plan = st.selectbox("Choose Plan", ["Free", "Silver", "Gold"])

if st.button("Upgrade Plan"):
    supabase.table("users").update({"plan": plan}).eq("email", email).execute()
    st.success(f"Plan updated to {plan}")

    if razorpay and plan != "Free":
        # Example Razorpay subscription (adjust PLAN_IDS & secret keys)
        PLAN_IDS = {"Silver":"plan_SFBUBSaO3jLhGL","Gold":"plan_SFBVQIj73B3joe"}
        client = razorpay.Client(auth=(st.secrets["RAZORPAY_KEY_ID"], st.secrets["RAZORPAY_KEY_SECRET"]))
        try:
            subscription = client.subscription.create({
                "plan_id": PLAN_IDS[plan],
                "customer_notify":1,
                "total_count":12
            })
            st.info(f"Razorpay subscription created. ID: {subscription['id']}")
        except Exception as e:
            st.error(f"Payment error: {e}")

# ---------------- Admin Dashboard ----------------
st.subheader("📊 Admin Dashboard")
users = supabase.table("users").select("*").execute().data

total_users = len(users)
paid_users = len([u for u in users if u["plan"] != "Free"])

st.metric("👥 Users", total_users)
st.metric("💎 Paid Users", paid_users)