import streamlit as st
import sqlite3
import pandas as pd
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from ai.coach import ask_atlas

# Page config
st.set_page_config(page_title="Project Atlas", page_icon="🏋️", layout="wide")

# Connect to database
conn = sqlite3.connect('data/atlas.db')

# Header
st.title("🏋️ Project Atlas")
st.subheader("Your Personal Training Intelligence Dashboard")

# ── Metric Cards ─────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_sets = pd.read_sql_query("SELECT COUNT(*) as count FROM sets WHERE set_type='normal'", conn).iloc[0]['count']
    st.metric("Total Sets Logged", f"{total_sets:,}")

with col2:
    st.metric("Squat PR", "420 lbs")

with col3:
    st.metric("Bench PR", "335 lbs")

with col4:
    st.metric("Trap Bar Deadlift PR", "455 lbs")

st.divider()

# ── Squat Progression Chart ───────────────────────────────────
st.subheader("📈 Squat Progression")
squat = pd.read_sql_query("""
    SELECT start_time as date, MAX(weight_lbs) as max_weight
    FROM sets
    WHERE exercise_title = 'Squat (Barbell)'
    AND set_type = 'normal'
    AND weight_lbs > 0
    GROUP BY start_time
    ORDER BY date
""", conn)
squat['date'] = pd.to_datetime(squat['date'], errors='coerce')
st.line_chart(squat.set_index('date')['max_weight'])

# ── Bench Progression Chart ───────────────────────────────────
st.subheader("📈 Bench Press Progression")
bench = pd.read_sql_query("""
    SELECT start_time as date, MAX(weight_lbs) as max_weight
    FROM sets
    WHERE exercise_title = 'Bench Press (Barbell)' 
    AND set_type = 'normal'
    AND weight_lbs > 0
    GROUP BY start_time
    ORDER BY date
""", conn)
bench['date'] = pd.to_datetime(bench['date'], errors='coerce')
st.line_chart(bench.set_index('date')['max_weight'])

# ── Volume by Workout Type ────────────────────────────────────
st.divider()
st.subheader("📊 Total Sets by Workout Type")
volume = pd.read_sql_query("""
    SELECT title, COUNT(*) as total_sets
    FROM sets
    WHERE set_type = 'normal'
    GROUP BY title
    ORDER BY total_sets DESC
""", conn)
st.bar_chart(volume.set_index('title')['total_sets'])

conn.close()

# ── AI Coach Chat ──────────────────────────────────────────────
st.divider()
st.subheader("🤖 Ask Atlas")
st.caption("Ask anything about your training — Atlas has your full history.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask Atlas a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Atlas is thinking..."):
            response = ask_atlas(prompt)
            st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})