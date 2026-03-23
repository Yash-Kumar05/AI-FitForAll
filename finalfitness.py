import os
import streamlit as st
import pandas as pd
import sqlite3
from datetime import date
from dotenv import load_dotenv
from groq import Groq
from fpdf import FPDF

# ================= LOAD ENV =================
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY not found")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# ================= PAGE CONFIG =================
st.set_page_config(page_title="AI FitForAll", layout="wide")

# ================= PREMIUM UI =================
st.markdown("""
<style>

.main {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
}

.glass {
    background: rgba(255,255,255,0.08);
    padding: 20px;
    border-radius: 20px;
    backdrop-filter: blur(12px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    margin-bottom: 20px;
}

.stTabs [data-baseweb="tab"] {
    background: rgba(255,255,255,0.1);
    border-radius: 15px;
    padding: 10px 20px;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg,#00c6ff,#0072ff);
    color: white !important;
    font-weight: bold;
}

.stButton>button {
    border-radius: 12px;
    background: linear-gradient(90deg,#ff9966,#ff5e62);
    color: white;
    font-weight: bold;
    border: none;
}

/* ---------- DAY CARDS ---------- */

.day-card {
    padding: 25px;
    border-radius: 22px;
    margin-bottom: 25px;
    box-shadow: 0 15px 40px rgba(0,0,0,0.4);
    transition: 0.4s ease;
}

.day-card:hover {
    transform: translateY(-5px);
}

.section-title {
    font-size: 28px;
    font-weight: bold;
    margin-bottom: 20px;
    text-align: center;
}

/* Workout gradients */
.workout-1 { background: linear-gradient(135deg,#ff512f,#dd2476); color:white; }
.workout-2 { background: linear-gradient(135deg,#11998e,#38ef7d); color:white; }
.workout-3 { background: linear-gradient(135deg,#396afc,#2948ff); color:white; }
.workout-4 { background: linear-gradient(135deg,#ee0979,#ff6a00); color:white; }
.workout-5 { background: linear-gradient(135deg,#00c6ff,#0072ff); color:white; }
.workout-6 { background: linear-gradient(135deg,#f7971e,#ffd200); color:white; }
.workout-7 { background: linear-gradient(135deg,#8e2de2,#4a00e0); color:white; }

/* Meal gradients */
.meal-1 { background: linear-gradient(135deg,#ff9a9e,#fad0c4); color:#222; }
.meal-2 { background: linear-gradient(135deg,#a18cd1,#fbc2eb); color:#222; }
.meal-3 { background: linear-gradient(135deg,#fbc2eb,#a6c1ee); color:#222; }
.meal-4 { background: linear-gradient(135deg,#fdcbf1,#e6dee9); color:#222; }
.meal-5 { background: linear-gradient(135deg,#84fab0,#8fd3f4); color:#222; }
.meal-6 { background: linear-gradient(135deg,#cfd9df,#e2ebf0); color:#222; }
.meal-7 { background: linear-gradient(135deg,#fccb90,#d57eeb); color:#222; }

footer {visibility: hidden;}

</style>
""", unsafe_allow_html=True)


# ================= DATABASE =================
conn = sqlite3.connect("fitness.db", check_same_thread=False)
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS progress (
    username TEXT,
    date TEXT,
    weight REAL
)""")

conn.commit()

# ================= SESSION =================
if "user" not in st.session_state:
    st.session_state.user = None

# ================= SIDEBAR DEV MODE =================
with st.sidebar:
    DEV_MODE = st.toggle("🛠 Developer Mode", False)

if DEV_MODE:
    st.session_state.user = "developer"

# ================= LOGIN =================
if st.session_state.user is None:

    st.title("🔐 AI Fitness Login")

    mode = st.radio("Mode", ["Login", "Register"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Submit"):

        if mode == "Register":
            try:
                c.execute(
                    "INSERT INTO users VALUES (?,?)",
                    (username, password)
                )
                conn.commit()
                st.success("Registered Successfully")

            except:
                st.error("User already exists")

        else:
            c.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (username, password)
            )

            if c.fetchone():
                st.session_state.user = username
                st.rerun()

            else:
                st.error("Invalid Credentials")

    st.stop()
# ================= SIDEBAR PROFILE =================
with st.sidebar:
    st.success(f"Logged in as {st.session_state.user}")
    if st.button("Logout"):
        st.session_state.user = None
        st.rerun()

    st.header("👤 Profile Settings")

    gender = st.selectbox("Gender", ["Male", "Female"])
    age = st.number_input("Age", 10, 80, 25)
    weight = st.number_input("Weight (kg)", 30.0, 200.0, 75.0)
    height = st.number_input("Height (cm)", 120.0, 220.0, 170.0)

    activity = st.selectbox("Activity Level",
        ["Sedentary", "Lightly Active", "Moderately Active", "Highly Active"])

    goal = st.radio("Goal", ["Weight Loss", "Weight Gain", "Maintenance"])

    level = st.selectbox("Fitness Level", ["Beginner", "Intermediate", "Advanced"])
    workout_time = st.slider("Workout Time (min)", 10, 120, 45)

    diet = st.selectbox("Diet Preference", ["Non-Vegetarian", "Vegetarian", "Vegan"])
    indian_mode = st.toggle("🇮🇳 Indian Diet Mode", False)

    coach_style = st.selectbox("AI Coach Style", ["Friendly", "Strict", "Motivational"])
    research_mode = st.toggle("🧠 Research Mode", False)

    generate = st.button("🚀 Generate AI FitForAll")

# ================= HEADER =================
st.markdown("""
<div style='text-align:center; padding:20px;'>
<h1>💪 AI FitForAll</h1>
<p>Scientific Engine + Behavioral Tracking + Adaptive Intelligence</p>
</div>
""", unsafe_allow_html=True)

# ================= SCIENCE =================
def calculate_bmr():
    if gender == "Male":
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161

activity_map = {
    "Sedentary": 1.2,
    "Lightly Active": 1.375,
    "Moderately Active": 1.55,
    "Highly Active": 1.725
}

bmr = calculate_bmr()
tdee = bmr * activity_map[activity]

if goal == "Weight Loss":
    target_calories = tdee - 400
elif goal == "Weight Gain":
    target_calories = tdee + 400
else:
    target_calories = tdee

protein = weight * 1.6

# ================= GENERATE PLAN =================
if generate:

    indian_line = "Use only Indian foods like roti, dal, paneer, rice, idli, dosa, poha, sabzi." if indian_mode else ""
    research_line = "Use scientific references." if research_mode else ""

    prompt = f"""
User: {age} year old {gender}
Goal: {goal}
Fitness Level: {level}
Workout Time: {workout_time} minutes
Diet: {diet}
Coach Style: {coach_style}

Calories: {int(target_calories)}
Protein: {int(protein)}g

{indian_line}
{research_line}

Create:
1. 7-day workout plan (only exercises, no meals)
2. 7-day meal plan (only food items)
3. Strategy improvement
4. Recovery tips
5. Motivation

Separate workout and meal sections clearly.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role":"system","content":"You are a certified Indian fitness expert."},
            {"role":"user","content":prompt}
        ],
        temperature=0.7,
        max_tokens=1500
    )

    st.session_state.plan = response.choices[0].message.content

# ================= TABS =================
tabs = st.tabs(["📋 AI Plan", "📈 Progress", "💬 Coach", "📊 Insights", "📄 Export"])

# -------- PLAN --------
with tabs[0]:
    if "plan" in st.session_state:

        plan_text = st.session_state.plan
        days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

        # -------- SPLIT WORKOUT & MEAL --------
        workout_part = plan_text
        meal_part = ""

        if "7-day meal" in plan_text.lower():
            parts = plan_text.lower().split("7-day meal")
            workout_part = plan_text[:len(parts[0])]
            meal_part = plan_text[len(parts[0]):]
        elif "meal plan" in plan_text.lower():
            parts = plan_text.lower().split("meal plan")
            workout_part = plan_text[:len(parts[0])]
            meal_part = plan_text[len(parts[0]):]

        # ================= WORKOUT SECTION =================
        st.markdown('<div class="section-title">🏋 7-Day Workout Plan</div>', unsafe_allow_html=True)

        for i, day in enumerate(days):
            if day in workout_part:
                try:
                    section = workout_part.split(day)[1]

                    for next_day in days[i+1:]:
                        if next_day in section:
                            section = section.split(next_day)[0]
                            break

                    # Convert lines to bullets
                    lines = section.strip().split("\n")
                    bullet_text = ""
                    for line in lines:
                        if line.strip():
                            bullet_text += f"- {line.strip()}\n"

                    st.markdown(f'<div class="day-card workout-{i+1}">', unsafe_allow_html=True)
                    st.markdown(f"### {day}")
                    st.markdown(bullet_text)
                    st.markdown("</div>", unsafe_allow_html=True)

                except:
                    pass

        # ================= MEAL SECTION =================
        st.markdown('<div class="section-title">🥗 7-Day Meal Plan</div>', unsafe_allow_html=True)

        for i, day in enumerate(days):
            if day in meal_part:
                try:
                    section = meal_part.split(day)[1]

                    for next_day in days[i+1:]:
                        if next_day in section:
                            section = section.split(next_day)[0]
                            break

                    lines = section.strip().split("\n")
                    bullet_text = ""
                    for line in lines:
                        if line.strip():
                            bullet_text += f"- {line.strip()}\n"

                    st.markdown(f'<div class="day-card meal-{i+1}">', unsafe_allow_html=True)
                    st.markdown(f"### {day}")
                    st.markdown(bullet_text)
                    st.markdown("</div>", unsafe_allow_html=True)

                except:
                    pass
# -------- PROGRESS --------
with tabs[1]:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    new_weight = st.number_input("Today's Weight", 30.0, 200.0, float(weight))
    if st.button("Log Progress"):
        c.execute("INSERT INTO progress VALUES (?,?,?)",
                  (st.session_state.user, str(date.today()), new_weight))
        conn.commit()
        st.success("Saved")

    df = pd.read_sql_query(
        f"SELECT date, weight FROM progress WHERE username='{st.session_state.user}'",
        conn
    )

    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
        st.line_chart(df.set_index("date")["weight"])
    st.markdown('</div>', unsafe_allow_html=True)

# -------- COACH CLEAN UI --------
with tabs[2]:
    st.markdown('<div class="glass">', unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for chat in st.session_state.chat_history:
        st.markdown(f"**{chat['role']}**: {chat['content']}")

user_msg = st.chat_input("Ask your AI Coach...")  

if user_msg:
        st.session_state.chat_history.append({"role":"You","content":user_msg})

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role":"user","content":user_msg}],
            temperature=0.7,
            max_tokens=500
        )

        ai_reply = response.choices[0].message.content
        st.session_state.chat_history.append({"role":"Coach","content":ai_reply})

        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# -------- INSIGHTS --------
with tabs[3]:
    col1,col2,col3,col4 = st.columns(4)
    col1.metric("BMI", round(weight / ((height/100)**2),1))
    col2.metric("BMR", int(bmr))
    col3.metric("TDEE", int(tdee))
    col4.metric("Target Calories", int(target_calories))

# -------- EXPORT --------
with tabs[4]:
    if "plan" in st.session_state:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        text = st.session_state.plan.encode("latin-1","ignore").decode("latin-1")
        pdf.multi_cell(0,8,text)
        pdf.output("plan.pdf")

        with open("plan.pdf","rb") as f:
            st.download_button("Download PDF", f, "FitnessPlan.pdf")

# ================= FOOTER =================
st.markdown("<hr><center>Built by Yash Kumar | AI FitForAll </center>", unsafe_allow_html=True)
