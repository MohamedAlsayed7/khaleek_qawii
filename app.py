import streamlit as st
import pandas as pd
import math
from datetime import datetime

st.set_page_config(page_title="Khaleek Qawi — Stay Strong", layout="centered")

# --- Helpers ---
@st.cache_data
def load_data():
    meals = pd.read_csv("data/meals.csv")
    exercises = pd.read_csv("data/exercises.csv")
    return meals, exercises

def mifflin_bmr(weight, height_cm, age, gender):
    s = -161 if gender.lower() == "female" else 5
    return 10*weight + 6.25*height_cm - 5*age + s

def activity_multiplier(level):
    mapping = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very": 1.9
    }
    return mapping.get(level, 1.55)

def choose_diet(preferences):
    diets_priority = ["keto","mediterranean","vegan","paleo","intermittent_fasting","low_carb","low_fat","balanced"]
    prefs = [p.lower() for p in preferences]
    for d in diets_priority:
        if d in prefs:
            return d
    return "balanced"

def macros_for_diet(key):
    mapping = {
        "keto": {"carbs":5, "protein":25, "fat":70},
        "mediterranean": {"carbs":40, "protein":20, "fat":40},
        "vegan": {"carbs":55, "protein":18, "fat":27},
        "paleo": {"carbs":35, "protein":30, "fat":35},
        "intermittent_fasting": {"carbs":40, "protein":25, "fat":35},
        "low_carb": {"carbs":30, "protein":30, "fat":40},
        "low_fat": {"carbs":55, "protein":20, "fat":25},
        "balanced": {"carbs":50, "protein":20, "fat":30},
    }
    return mapping.get(key, mapping["balanced"])

def generate_plan(user, meals_df, exercises_df):
    age = user["age"]
    height_cm = user["height_cm"]
    weight_kg = user["weight_kg"]
    goal = user["goal"]
    activity = user["activity_level"]
    prefs = user.get("dietary_preferences", [])

    bmr = mifflin_bmr(weight_kg, height_cm, age, user["gender"])
    tdee = math.floor(bmr * activity_multiplier(activity))

    if goal == "lose":
        calories = max(1000, tdee - 500)
    elif goal == "gain":
        calories = tdee + 400
    else:
        calories = tdee

    diet = choose_diet(prefs)
    macros = macros_for_diet(diet)
    protein_g = round((calories * macros["protein"]/100) / 4)
    carbs_g = round((calories * macros["carbs"]/100) / 4)
    fats_g = round((calories * macros["fat"]/100) / 9)

    available_meals = meals_df.copy()

    meals = available_meals.sample(n=3, replace=True).to_dict(orient="records")
    snack = available_meals.sample(n=1).to_dict(orient="records")[0]

    if goal == "lose":
        pool = exercises_df[exercises_df["type"].isin(["cardio","hiit","full_body"])]
    elif goal == "gain":
        pool = exercises_df[exercises_df["type"].isin(["strength","hypertrophy","compound"])]
    else:
        pool = exercises_df.copy()

    days = 4 if activity in ["sedentary","light"] else 5 if activity=="moderate" else 6
    weekly = []
    for d in range(days):
        picks = pool.sample(n=min(4, len(pool))).to_dict(orient="records")
        weekly.append({
            "day": d+1,
            "duration_min": 40 if goal=="lose" else 60,
            "exercises": picks
        })

    return {
        "generatedAt": datetime.utcnow().isoformat() + "Z",
        "summary": {
            "calories": calories,
            "macros": {"protein_g": protein_g, "carbs_g": carbs_g, "fats_g": fats_g},
            "diet": diet,
            "days_per_week": days,
            "goal": goal
        },
        "meals": meals,
        "snack": snack,
        "workouts": weekly,
        "notes": "This plan is demo-generated. For medical or special nutrition needs consult a professional."
    }

# --- App UI ---
st.title("Khaleek Qawi — Stay Strong (Demo)")
st.markdown("Personalized diet & workout plan generator — **English UI**.")

meals_df, exercises_df = load_data()

with st.expander("How it works (short)"):
    st.write("""
    1. Enter client's basic data (age, height, weight, goal, activity).
    2. Choose dietary preferences (optional).
    3. Generate a sample diet + workout plan. Update metrics later to re-generate.
    """)

st.header("Client Information")
col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Full name", value="Test Client")
    age = st.number_input("Age", min_value=12, max_value=100, value=30)
    gender = st.selectbox("Gender", ["male","female"])
    height_cm = st.number_input("Height (cm)", min_value=100, max_value=230, value=175)
with col2:
    weight_kg = st.number_input("Weight (kg)", min_value=30.0, max_value=250.0, value=80.0, step=0.1)
    goal = st.selectbox("Goal", ["maintain","lose","gain"])
    activity_level = st.selectbox("Activity level", ["sedentary","light","moderate","active","very"])
    prefs_raw = st.text_input("Dietary preferences (comma separated keys, e.g. vegan,keto)", value="balanced")

dietary_preferences = [p.strip() for p in prefs_raw.split(",") if p.strip()]

if st.button("Generate Plan"):
    user = {
        "name": name,
        "age": int(age),
        "gender": gender,
        "height_cm": int(height_cm),
        "weight_kg": float(weight_kg),
        "goal": goal,
        "activity_level": activity_level,
        "dietary_preferences": dietary_preferences
    }
    plan = generate_plan(user, meals_df, exercises_df)
    st.success("Plan generated ✔️")

    st.subheader("Summary")
    st.write(plan["summary"])

    st.subheader("Meals (outline)")
    for m in plan["meals"]:
        st.markdown(f"- **{m['title']}** — {m['description']}")

    st.markdown(f"**Snack:** {plan['snack']['title']} — {plan['snack']['description']}")

    st.subheader("Weekly Workouts")
    for w in plan["workouts"]:
        st.markdown(f"**Day {w['day']} — {w['duration_min']} min**")
        for ex in w["exercises"]:
            st.write(f"- {ex['name']} — {ex['instructions']}")

    st.subheader("Macros (grams)")
    st.write(plan["summary"]["macros"])

    st.info(plan["notes"])

st.markdown('---')
st.caption("Demo app — made for quick testing and deployment to Streamlit Cloud. Code is simple and meant to be extended.")
