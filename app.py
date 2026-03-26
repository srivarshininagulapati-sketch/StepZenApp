import streamlit as st
import requests
import google.generativeai as genai
from gtts import gTTS

# ---------------- Optional Razorpay ----------------
try:
    import razorpay
except:
    razorpay = None
    st.warning("Razorpay not installed")

# ---------------- Config ----------------
st.set_page_config(page_title="ZenChat AI", layout="wide")

# ---------------- Secrets ----------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# ---------------- Supabase ----------------
def supabase_get(table, col=None, val=None):
    url = f"{SUPABASE_URL}/{table}"
    if col and val:
        url += f"?{col}=eq.{val}"
    r = requests.get(url, headers=headers)
    return r.json() if r.status_code == 200 else []

def supabase_insert(table, data):
    r = requests.post(f"{SUPABASE_URL}/{table}", headers=headers, json=data)
    return r.json()

def supabase_delete(table, col, val):
    requests.delete(f"{SUPABASE_URL}/{table}?{col}=eq.{val}", headers=headers)

# ---------------- AI ----------------
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

SYSTEM_PROMPT = "You are friendly AI assistant."

# ---------------- Login ----------------
st.sidebar.title("Login")
email = st.sidebar.text_input("Email")
if not email:
    st.stop()

# ---------------- User ----------------
user = supabase_get("users", "email", email)
if user:
    user = user[0]
else:
    user = {"email": email, "plan": "Free", "habits": []}
    supabase_insert("users", user)

# ---------------- Chat Sessions ----------------
st.sidebar.subheader("Chats")
sessions = supabase_get("chat_sessions", "user_id", email)

if st.sidebar.button("New Chat"):
    supabase_insert("chat_sessions", {"user_id": email, "title": "New Chat"})
    st.rerun()

selected_session = None
for s in sessions:
    if st.sidebar.button(s["title"], key=s["id"]):
        selected_session = s["id"]

# ensure session
if not selected_session:
    new = supabase_insert("chat_sessions", {"user_id": email, "title": "New Chat"})
    selected_session = new[0]["id"]

# ---------------- UI ----------------
st.title("ZenChat AI")

# ---------------- Chat ----------------
messages = supabase_get("messages", "session_id", selected_session)

for m in messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

prompt = st.chat_input("Type...")
if prompt:
    supabase_insert("messages", {
        "session_id": selected_session,
        "role": "user",
        "content": prompt
    })

    try:
        res = model.generate_content(prompt)
        ans = res.text
    except Exception as e:
        ans = str(e)

    supabase_insert("messages", {
        "session_id": selected_session,
        "role": "assistant",
        "content": ans
    })

    tts = gTTS(ans)
    tts.save("voice.mp3")
    st.audio("voice.mp3")

    st.rerun()