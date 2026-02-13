import streamlit as st
import datetime
from supabase import create_client
import google.generativeai as genai
import razorpay

# ----------------------------
# SECRETS (SAFE, LOCAL)
# ----------------------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
RAZORPAY_KEY_ID = st.secrets["RAZORPAY_KEY_ID"]
RAZORPAY_KEY_SECRET = st.secrets["RAZORPAY_KEY_SECRET"]

# ----------------------------
# DATABASE
# ----------------------------
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ----------------------------
# GOOGLE AI
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
    "Silver": {"daily_limit": 100, "price": 199, "plan_SFBUBSaO3jLhGL": "plan_silver"},
    "Gold": {"daily_limit": 400, "price": 399, "plan_SFBVQIj73B3joe": "plan_gold"},
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
# LOAD USER
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

st.write(f"Current Plan: {user['plan']}")
st.write(f"Chats Used Today: {user['chats_today']} / {PLANS[user['plan']]['daily_limit']}")

# ----------------------------
# HABIT TRACKER
# ----------------------------
st.subheader("📅 Habit Tracker")
new_habit = st.text_input("Add New Habit")
if st.button("Add Habit") and new_habit:
    user["habits"].append(new_habit)
    supabase.table("users").update({"habits": user["habits"]}).eq("email", email).execute()
    st.experimental_rerun()

for i, h in enumerate(user["habits"]):
    st.write(f"✔️ {h}")
    if st.button(f"Delete", key=f"habit_del_{i}"):
        user["habits"].pop(i)
        supabase.table("users").update({"habits": user["habits"]}).eq("email", email).execute()
        st.experimental_rerun()

# ----------------------------
# AI CHAT
# ----------------------------
st.subheader("🤖 AI Chat")
question = st.text_input("Ask something")
if st.button("Send") and question:
    if user["chats_today"] >= PLANS[user["plan"]]["daily_limit"]:
        st.error("Daily chat limit reached. Upgrade plan.")
    else:
        try:
            response = model.generate_content(question)
            response_text = response.text
        except Exception as e:
            response_text = f"Error: {str(e)}"

        user["chats"].append({"Q": question, "A": response_text})
        user["chats_today"] += 1

        supabase.table("users").update({
            "chats": user["chats"],
            "chats_today": user["chats_today"]
        }).eq("email", email).execute()

        st.experimental_rerun()

# ----------------------------
# CHAT HISTORY
# ----------------------------
st.subheader("💬 Chat History")
for i, c in enumerate(user["chats"]):
    st.markdown(f"**Q:** {c['Q']}")
    st.markdown(f"**A:** {c['A']}")
    if st.button("Delete", key=f"chat_del_{i}"):
        user["chats"].pop(i)
        supabase.table("users").update({"chats": user["chats"]}).eq("email", email).execute()
        st.experimental_rerun()
    st.markdown("---")

# ----------------------------
# UPGRADE PLAN WITH RAZORPAY PAYMENT
# ----------------------------
st.subheader("💎 Upgrade Plan")
selected_plan = st.radio("Choose Plan", ["Free", "Silver", "Gold"])
plan_info = PLANS[selected_plan]
st.write(f"Daily Chat Limit: {plan_info['daily_limit']}")
st.write(f"Price per month: ₹{plan_info['price']}")

if st.button("Activate Plan"):
    if plan_info["price"] == 0:
        # Free plan
        user["plan"] = "Free"
        supabase.table("users").update({"plan": "Free"}).eq("email", email).execute()
        st.success("Plan updated to Free")
    else:
        try:
            # Razorpay subscription
            subscription = rz_client.subscription.create({
                "plan_id": plan_info["plan_id"],
                "customer_notify": 1,
                "total_count": 12
            })
            user["plan"] = selected_plan
            supabase.table("users").update({"plan": selected_plan}).eq("email", email).execute()
            st.success(f"Subscribed to {selected_plan}! Payment created successfully.")
        except Exception as e:
            st.error(f"Razorpay payment failed: {str(e)}")

    st.experimental_rerun()

# ----------------------------
# EXPORT DATA
# ----------------------------
st.subheader("💾 Export Data")
if st.button("Download JSON"):
    st.download_button(
        label="Download",
        data=str(user),
        file_name="user_data.json",
        mime="application/json"
    )
