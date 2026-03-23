import os
import streamlit as st
import pandas as pd
import sqlite3
import numpy as np
from datetime import date
from dotenv import load_dotenv
from groq import Groq
from fpdf import FPDF
from sklearn.linear_model import LinearRegression

# ================= LOAD ENV =================
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY not found")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# ================= PAGE CONFIG =================
st.set_page_config(page_title="AI Fitness Club", layout="wide")

# ================= PREMIUM UI =================
st.markdown("""
<style>
body {
    background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
    color: white;
}
.glass {
    background: rgba(255,255,255,0.08);
    padding: 25px;
    border-radius: 20px;
    backdrop-filter: blur(12px);
    margin-bottom:20px;
}
.header-bar {
    height:18px;
    border-radius:20px;
    background:linear-gradient(90deg,#ff512f,#dd2476);
    margin-bottom:25px;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg,#00c6ff,#0072ff);
    color:white !important;
}
footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ================= DATABASE =================
conn = sqlite3.connect("fitness.db", check_same_thread=False)
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS users(
    username TEXT PRIMARY KEY,
    password TEXT)""")

c.execute("""CREATE TABLE IF NOT EXISTS progress(
    username TEXT,
    date TEXT,
    weight REAL)""")

c.execute("""CREATE TABLE IF NOT EXISTS habits(
    username TEXT,
    date TEXT,
    water INTEGER,
    sleep REAL,
    steps INTEGER)""")

c.execute("""CREATE TABLE IF NOT EXISTS subscription(
    username TEXT PRIMARY KEY,
    plan TEXT)""")

conn.commit()

# ================= SESSION =================
if "user" not in st.session_state:
    st.session_state.user = None

# ================= SIDEBAR =================
with st.sidebar:

    DEV_MODE = st.toggle("🛠 Developer Mode")

    if DEV_MODE:
        st.session_state.user = "developer"

    if st.session_state.user:
        st.success(f"Logged in as {st.session_state.user}")
        if st.button("Logout"):
            st.session_state.user = None
            st.rerun()

# ================= LOGIN =================
if st.session_state.user is None:
    st.title("🔐 AI Fitness Club login")
    mode = st.radio("Mode", ["Login","Register"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Submit"):
        if mode=="Register":
            try:
                c.execute("INSERT INTO users VALUES (?,?)",(username,password))
                conn.commit()
                st.success("Registered!")
            except:
                st.error("User exists")
        else:
            c.execute("SELECT * FROM users WHERE username=? AND password=?",
                      (username,password))
            if c.fetchone():
                st.session_state.user=username
                st.rerun()
            else:
                st.error("Invalid login")
    st.stop()

# ================= SUBSCRIPTION =================
c.execute("SELECT plan FROM subscription WHERE username=?",
          (st.session_state.user,))
data=c.fetchone()

if not data:
    c.execute("INSERT INTO subscription VALUES (?,?)",
              (st.session_state.user,"Free"))
    conn.commit()
    user_plan="Free"
else:
    user_plan=data[0]

st.sidebar.markdown(f"### 💎 Plan: {user_plan}")
if user_plan=="Free":
    if st.sidebar.button("Upgrade to Pro"):
        c.execute("UPDATE subscription SET plan='Pro' WHERE username=?",
                  (st.session_state.user,))
        conn.commit()
        st.sidebar.success("Upgraded 🚀")
        st.rerun()

# ================= PROFILE =================
with st.sidebar:
    gender=st.selectbox("Gender",["Male","Female"])
    age=st.number_input("Age",10,80,25)
    weight=st.number_input("Weight",30.0,200.0,75.0)
    height=st.number_input("Height",120.0,220.0,170.0)
    activity=st.selectbox("Activity",
        ["Sedentary","Lightly Active","Moderately Active","Highly Active"])
    goal=st.radio("Goal",
        ["Weight Loss","Weight Gain","Maintenance"])
    indian_mode=st.toggle("🇮🇳 Indian Diet Mode")
    research_mode=st.toggle("🧠 Research Mode")
    generate=st.button("🚀 Generate Plan")

# ================= HEADER =================
st.markdown("<h1 style='text-align:center;'>💪 AI Fitness Club</h1>",
            unsafe_allow_html=True)
st.markdown('<div class="header-bar"></div>',unsafe_allow_html=True)

# ================= SCIENCE ENGINE =================
def bmr_calc():
    if gender=="Male":
        return 10*weight+6.25*height-5*age+5
    return 10*weight+6.25*height-5*age-161

activity_map={
    "Sedentary":1.2,
    "Lightly Active":1.375,
    "Moderately Active":1.55,
    "Highly Active":1.725}

bmr=bmr_calc()
tdee=bmr*activity_map[activity]

if goal=="Weight Loss":
    target=tdee-400
elif goal=="Weight Gain":
    target=tdee+400
else:
    target=tdee

# ================= ADAPTIVE ENGINE =================
df_progress=pd.read_sql_query(
    f"SELECT weight FROM progress WHERE username='{st.session_state.user}'",
    conn)

if len(df_progress)>=7 and goal=="Weight Loss":
    recent=df_progress.tail(7)["weight"]
    if recent.max()-recent.min()<0.3:
        target-=200
        st.info("🔁 Adaptive Engine Activated (-200 cal)")

# ================= GENERATE PLAN =================
if generate:
    indian_line="Use only Indian foods." if indian_mode else ""
    research_line="Add scientific references." if research_mode else ""

    prompt=f"""
Goal:{goal}
Calories:{int(target)}
{indian_line}
{research_line}
Create 7 day plan + meal plan + motivation.
"""

    res=client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role":"user","content":prompt}],
        temperature=0.7,
        max_tokens=1200)

    st.session_state.plan=res.choices[0].message.content

# ================= TABS =================
tabs=st.tabs(["📋 Plan","📈 Progress","🔥 Habits","📊 Insights","📄 Export"])

# -------- PLAN --------
with tabs[0]:
    if "plan" in st.session_state:
        st.markdown('<div class="glass">',unsafe_allow_html=True)
        st.markdown(st.session_state.plan)
        st.markdown('</div>',unsafe_allow_html=True)

        if st.button("🛒 Generate Grocery List"):
            g_prompt="Make grocery list for:\n"+st.session_state.plan
            g_res=client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role":"user","content":g_prompt}],
                temperature=0.7,
                max_tokens=500)
            st.write(g_res.choices[0].message.content)

# -------- PROGRESS --------
with tabs[1]:
    new_weight=st.number_input("Today's Weight",30.0,200.0,weight)
    if st.button("Log Weight"):
        c.execute("INSERT INTO progress VALUES (?,?,?)",
                  (st.session_state.user,str(date.today()),new_weight))
        conn.commit()
        st.success("Saved")

    df=pd.read_sql_query(
        f"SELECT date,weight FROM progress WHERE username='{st.session_state.user}'",
        conn)

    if not df.empty:
        df["date"]=pd.to_datetime(df["date"])
        st.line_chart(df.set_index("date")["weight"])

# -------- HABITS --------
with tabs[2]:
    water=st.number_input("Water Glasses",0,20,8)
    sleep=st.number_input("Sleep Hours",0.0,12.0,7.0)
    steps=st.number_input("Steps",0,50000,5000)

    if st.button("Save Habits"):
        c.execute("INSERT INTO habits VALUES (?,?,?,?,?)",
                  (st.session_state.user,str(date.today()),water,sleep,steps))
        conn.commit()
        st.success("Saved")

    hdf=pd.read_sql_query(
        f"SELECT * FROM habits WHERE username='{st.session_state.user}'",
        conn)

    if not hdf.empty:
        score=(hdf["water"].mean()/8)*30+(hdf["sleep"].mean()/7)*30+(hdf["steps"].mean()/8000)*40
        st.metric("Consistency Score",f"{int(score)}/100")

# -------- INSIGHTS --------
with tabs[3]:
    col1,col2,col3,col4=st.columns(4)
    col1.metric("BMI",round(weight/((height/100)**2),1))
    col2.metric("BMR",int(bmr))
    col3.metric("TDEE",int(tdee))
    col4.metric("Target Cal",int(target))

    if len(df_progress)>5:
        df_full=pd.read_sql_query(
            f"SELECT date,weight FROM progress WHERE username='{st.session_state.user}'",
            conn)
        df_full["day"]=range(len(df_full))
        X=np.array(df_full["day"]).reshape(-1,1)
        y=df_full["weight"]
        model=LinearRegression().fit(X,y)
        future=model.predict([[len(df_full)+7]])[0]
        st.metric("Predicted Weight (Next Week)",round(future,1))

# -------- EXPORT --------
with tabs[4]:
    if "plan" in st.session_state:
        pdf=FPDF()
        pdf.add_page()
        pdf.set_font("Arial",size=10)
        text=st.session_state.plan.encode("latin-1","ignore").decode("latin-1")
        pdf.multi_cell(0,8,text)
        pdf.output("plan.pdf")

        with open("plan.pdf","rb") as f:
            st.download_button("Download PDF",f,"FitnessPlan.pdf")

# ================= FOOTER =================
st.markdown("<hr><center>Built with ❤️ by Riya Kumari | AI Fitness Club</center>",
            unsafe_allow_html=True)
