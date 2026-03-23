import os
import random
import datetime
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
from fpdf import FPDF

# ================= LOAD ENV =================
load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    st.error("❌ GOOGLE_API_KEY not found in .env file.")
    st.stop()

genai.configure(api_key=API_KEY)

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="AI Fitness Assistant",
    page_icon="💪",
    layout="wide"
)

# ================= STYLE =================
st.markdown("""
<style>
body { background-color: #0f1117; }
h1, h2, h3 { color: #22c55e; }
.stButton>button { background-color: #22c55e; color: white; border-radius: 8px; width: 100%; }
</style>
""", unsafe_allow_html=True)

# ================= TITLE =================
st.title("💪 AI Fitness & Wellness Dashboard")
st.caption("Clean • Smart • AI Powered")

# ================= MODEL =================
@st.cache_resource
def load_model():
    # FIXED: Using the full model path to avoid 404 errors
    return genai.GenerativeModel("models/gemini-1.5-flash")

model = load_model()

# ================= SIDEBAR =================
with st.sidebar:
    st.header("👤 Profile")
    
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    age = st.number_input("Age", 10, 80, 25)
    weight = st.number_input("Weight (kg)", 30.0, 200.0, 75.0)
    height = st.number_input("Height (cm)", 120.0, 220.0, 170.0)

    activity = st.selectbox(
        "Activity Level",
        ["Sedentary", "Lightly Active", "Moderately Active", "Highly Active"]
    )

    goal = st.radio("Goal", ["Weight Loss", "Weight Gain", "Maintenance"])
    level = st.selectbox("Fitness Level", ["Beginner", "Intermediate", "Advanced"])
    time = st.slider("Workout Time (min)", 10, 120, 45)

    diet = st.selectbox("Diet", ["Non-Vegetarian", "Vegetarian", "Vegan"])
    indian_mode = st.toggle("🇮🇳 Indian Diet Mode", True)
    coach = st.selectbox("🤖 AI Coach Style", ["Friendly", "Strict", "Motivational"])

    generate = st.button("🚀 Generate My Plan")

# ================= METRICS =================
bmi = weight / ((height / 100) ** 2)

c1, c2, c3 = st.columns(3)
c1.metric("BMI", f"{bmi:.1f}")
c2.metric("Goal", goal)
c3.metric("Workout Time", f"{time} min")

# ================= PROMPT =================
def build_prompt():
    return f"""
    You are a professional fitness coach. 
    User Profile: Age {age}, Gender {gender}, Weight {weight}kg, Height {height}cm, BMI {bmi:.1f}.
    Context: Activity Level: {activity}, Goal: {goal}, Level: {level}, Diet: {diet}, Indian Diet Mode: {indian_mode}.
    Coach Personality: {coach}.
    
    Provide:
    1. A weekly workout schedule for {time} min sessions.
    2. A daily meal plan.
    3. Essential lifestyle habits.
    4. Safety warnings.
    """

# ================= GENERATE =================
if generate:
    with st.spinner("🧠 AI is crafting your personalized plan..."):
        try:
            # We use the model instance directly
            response = model.generate_content(build_prompt())
            st.session_state["plan"] = response.text
        except Exception as e:
            st.error(f"Generation Error: {e}")

# ================= TABS =================
tabs = st.tabs(["📋 Your Plan", "🌱 Daily Habits", "🔥 Motivation", "📊 Insights", "🧾 Profile Summary"])

with tabs[0]:
    if "plan" in st.session_state:
        st.markdown(st.session_state["plan"])
    else:
        st.info("👈 Fill in your details and click 'Generate My Plan' to start!")

with tabs[1]:
    st.checkbox("💧 Drink 3-4 Liters of Water")
    st.checkbox("🧘 5-10 min Morning Stretching")
    st.checkbox("😴 7-8 hours of quality sleep")

with tabs[2]:
    st.success(random.choice([
        "Consistency beats perfection. 🔥",
        "Your only limit is you. 💚",
        "No excuses! 💪"
    ]))

with tabs[3]:
    st.metric("Recommended Protein (g)", int(weight * 1.6))
    st.metric("Target Water (Liters)", round(weight * 0.035, 1))

with tabs[4]:
    st.write(f"**Current Stats:**\n- Gender: {gender}\n- Age: {age}\n- Weight: {weight}kg\n- BMI: {bmi:.1f}\n- Goal: {goal}")

# ================= PDF DOWNLOAD =================
if "plan" in st.session_state:
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=11)
        clean_text = st.session_state["plan"].encode('latin-1', 'ignore').decode('latin-1')
        pdf.multi_cell(0, 10, clean_text)
        pdf.output("fitness_plan.pdf")

        with open("fitness_plan.pdf", "rb") as f:
            st.download_button(
                label="⬇️ Download Plan as PDF",
                data=f,
                file_name="My_AI_Fitness_Plan.pdf",
                mime="application/pdf"
            )
    except Exception as e:
        st.warning("Note: PDF generated without icons/emojis for compatibility.")