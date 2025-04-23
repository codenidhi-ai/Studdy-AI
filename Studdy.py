import streamlit as st
import time
from datetime import datetime, timedelta, date
import pandas as pd
import calendar
import random

# --- Page Config ---
st.set_page_config(page_title="Studdy", page_icon="📚", layout="wide")

# --- Styling ---
st.markdown("""
    <style>
        body { background-color: #f9fbfd; }
        .main { font-family: 'Segoe UI', sans-serif; }
        .scheduler-scroll { max-height: 300px; overflow-y: auto; padding-right: 10px; }
        .habit-box button { width: 100%; font-size: 0.9em; }
    </style>
""", unsafe_allow_html=True)

# --- Logo and Header ---
st.image("logo-icon.png", width=80)
st.markdown("<h1 style='text-align: center;'>STUDDY</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: orange;'>Study smarter, not harder</h4>", unsafe_allow_html=True)
st.markdown("---")

# --- Motivation Quote ---
quotes = [
    "Push yourself, because no one else is going to do it for you.",
    "Success doesn’t just find you. You have to go out and get it.",
    "It always seems impossible until it’s done.",
    "Great things never come from comfort zones.",
    "Dream it. Wish it. Do it.",
    "Don’t watch the clock; do what it does. Keep going."
]
st.info(f"💡 Motivation: {random.choice(quotes)}")

# --- Session States ---
def init_state():
    default_states = {
        "tasks": {"personal": [], "work": []},
        "notes": "",
        "habits": {},
        "timer_active": False,
        "timer_end": None,
        "goals": [],
        "study_data": [],
        "confetti_task": False,
        "balloon_goal": False
    }
    for k, v in default_states.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# --- Pomodoro Timer ---
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    st.subheader("🍅 Pomodoro Timer")
    work_duration = st.slider("Work Duration (min)", 1, 60, 25)
    break_duration = st.slider("Break Duration (min)", 1, 30, 5)
    if st.button("Start Timer"):
        st.session_state.timer_end = datetime.now() + timedelta(minutes=work_duration)
        st.session_state.timer_active = True

    if st.session_state.timer_active:
        remaining = st.session_state.timer_end - datetime.now()
        if remaining.total_seconds() > 0:
            mins, secs = divmod(int(remaining.total_seconds()), 60)
            st.info(f"⏳ {mins:02d}:{secs:02d} remaining")
            time.sleep(1)
            st.experimental_rerun()
        else:
            st.session_state.timer_active = False
            st.success("⏰ Time's up! Take a break!")
            st.balloons()

# --- Habit Tracker ---
with col2:
    st.subheader("📈 Habit Tracker")
    habit_name = st.text_input("Habit Name")
    today = date.today()
    selected_dates = st.session_state.habits.get(habit_name, set())

    week_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    st.markdown("| " + " | ".join([f"**{d}**" for d in week_days]) + " |")
    st.markdown("|---" * 7 + "|")

    for week in calendar.monthcalendar(today.year, today.month):
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day != 0:
                day_date = date(today.year, today.month, day)
                label = f"✅ {day}" if day_date in selected_dates else f"{day}"
                if cols[i].button(label, key=f"habit_{habit_name}_{day}"):
                    selected_dates = selected_dates.symmetric_difference({day_date})
    if habit_name:
        st.session_state.habits[habit_name] = selected_dates

# --- Daily Scheduler ---
with col3:
    st.subheader("📅 Scheduler")
    current_day = st.date_input("Date", value=date.today())
    event_key = str(current_day)
    if event_key not in st.session_state:
        st.session_state[event_key] = []

    time_slot = st.selectbox("Time", [f"{h:02d}:00" for h in range(24)])
    event = st.text_input("Task")
    if st.button("Add Event"):
        if event:
            st.session_state[event_key].append({"time": time_slot, "event": event})

    st.markdown("<div class='scheduler-scroll'>", unsafe_allow_html=True)
    for e in sorted(st.session_state[event_key], key=lambda x: x['time']):
        st.write(f"🕒 {e['time']} - {e['event']}")
    st.markdown("</div>", unsafe_allow_html=True)

# --- Tasks and Notes ---
col4, col5 = st.columns(2)
with col4:
    st.subheader("✅ Tasks")
    for cat in ["personal", "work"]:
        st.markdown(f"**{cat.capitalize()}**")
        new_task = st.text_input(f"New {cat} task", key=f"task_{cat}")
        if st.button(f"Add {cat}", key=f"btn_{cat}"):
            if new_task:
                st.session_state.tasks[cat].append({"task": new_task, "done": False})

        for i, t in enumerate(st.session_state.tasks[cat]):
            c1, c2 = st.columns([0.1, 0.9])
            prev_status = t["done"]
            t["done"] = c1.checkbox("", value=t["done"], key=f"chk_{cat}_{i}")
            c2.markdown(f"~~{t['task']}~~" if t["done"] else t["task"])
            if not prev_status and t["done"]:
                st.session_state.confetti_task = True

    if st.session_state.confetti_task:
        st.snow()
        st.session_state.confetti_task = False

with col5:
    st.subheader("📝 Notes")
    st.session_state.notes = st.text_area("Quick Notes", value=st.session_state.notes, height=250)

# --- Study Goals ---
st.markdown("---")
st.subheader("🎯 Study Goals")
goal_input = st.text_input("New Goal")
if st.button("Add Goal"):
    if goal_input:
        st.session_state.goals.append({"goal": goal_input, "achieved": False})
        st.session_state.study_data.append({"date": date.today(), "count": len([g for g in st.session_state.goals if g['achieved']])})

for i, g in enumerate(st.session_state.goals):
    c1, c2 = st.columns([0.1, 0.9])
    prev = g["achieved"]
    g["achieved"] = c1.checkbox("", value=g["achieved"], key=f"goal_{i}")
    c2.markdown(f"✅ {g['goal']}" if g["achieved"] else f"🔹 {g['goal']}")
    if not prev and g["achieved"]:
        st.session_state.balloon_goal = True

if st.session_state.balloon_goal:
    st.balloons()
    st.session_state.balloon_goal = False

if st.session_state.study_data:
    df = pd.DataFrame(st.session_state.study_data)
    df = df.groupby("date").count().reset_index()
    df.columns = ["Date", "Goals Achieved"]
    st.line_chart(df.set_index("Date"))
