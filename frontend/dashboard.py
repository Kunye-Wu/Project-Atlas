import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from ai.coach import ask_atlas
from backend.plateau_detector import detect_plateaus

st.set_page_config(page_title="Project Atlas", page_icon="🏋️", layout="wide")

conn = sqlite3.connect('data/atlas.db')

# ── Header ────────────────────────────────────────────────────
st.title("🏋️ Project Atlas")
st.subheader("Your Personal Training Intelligence Dashboard")

# ── Metric Cards ──────────────────────────────────────────────
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

# ── Plateau Detection ─────────────────────────────────────────
st.subheader("🔍 Plateau & Progress Monitor")
plateau_data = detect_plateaus()
cols = st.columns(3)
col_idx = 0
for lift, data in plateau_data.items():
    with cols[col_idx % 3]:
        if data['plateau']:
            st.error(f"⚠️ {lift}\n\ne1RM: {data['first_e1rm']} → {data['last_e1rm']} lbs\n\n{data['pct_change']:+.1f}% over {data['sessions_analyzed']} sessions")
        else:
            st.success(f"✅ {lift}\n\ne1RM: {data['first_e1rm']} → {data['last_e1rm']} lbs\n\n{data['pct_change']:+.1f}% over {data['sessions_analyzed']} sessions")
    col_idx += 1

st.divider()

# ── Exercise Selector Chart ───────────────────────────────────
st.subheader("📈 Exercise Progression")

all_exercises = pd.read_sql_query("""
    SELECT DISTINCT exercise_title
    FROM sets
    WHERE set_type = 'normal' AND weight_lbs > 0
    ORDER BY exercise_title
""", conn)

exercise_list = all_exercises['exercise_title'].tolist()
default_idx = exercise_list.index('Squat (Barbell)') if 'Squat (Barbell)' in exercise_list else 0
selected_exercise = st.selectbox("Select an exercise:", exercise_list, index=default_idx)

exercise_data = pd.read_sql_query(f"""
    SELECT start_time as date, MAX(weight_lbs) as max_weight
    FROM sets
    WHERE exercise_title = '{selected_exercise}'
    AND set_type = 'normal' AND weight_lbs > 0
    GROUP BY date
    ORDER BY date
""", conn)

exercise_data['date'] = pd.to_datetime(exercise_data['date'], errors='coerce')
exercise_data = exercise_data.dropna(subset=['date'])
exercise_data = exercise_data.sort_values('date').reset_index(drop=True)

# PR detection — mark any session where a new all-time max is set
exercise_data['prev_max'] = exercise_data['max_weight'].shift(1).fillna(0)
exercise_data['running_max'] = exercise_data['max_weight'].cummax()
exercise_data['is_pr'] = exercise_data['max_weight'] > exercise_data['prev_max'].cummax()
pr_points = exercise_data[exercise_data['is_pr']]

fig = go.Figure()

# Main progression line
fig.add_trace(go.Scatter(
    x=exercise_data['date'],
    y=exercise_data['max_weight'],
    mode='lines',
    name='Max Weight',
    line=dict(color='#4C9BE8', width=2)
))

# PR markers
fig.add_trace(go.Scatter(
    x=pr_points['date'],
    y=pr_points['max_weight'],
    mode='markers',
    name='PR ⭐',
    marker=dict(color='gold', size=10, symbol='star'),
    text=[f"PR: {w} lbs" for w in pr_points['max_weight']],
    hovertemplate='%{text}<br>%{x}<extra></extra>'
))

fig.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)'),
    legend=dict(orientation='h', yanchor='bottom', y=1.02),
    margin=dict(l=0, r=0, t=30, b=0),
    height=400
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Volume by Workout Type ────────────────────────────────────
st.subheader("📊 Total Sets by Workout Type")
volume = pd.read_sql_query("""
    SELECT title, COUNT(*) as total_sets
    FROM sets WHERE set_type = 'normal'
    GROUP BY title ORDER BY total_sets DESC
""", conn)
st.bar_chart(volume.set_index('title')['total_sets'])

st.divider()

# ── Athlete Notes ─────────────────────────────────────────────
st.subheader("📝 Athlete Notes")
st.caption("Log context Atlas can't see in the data — injuries, sleep, life stuff.")

notes_conn = sqlite3.connect('data/atlas.db')
notes_conn.execute("""
    CREATE TABLE IF NOT EXISTS athlete_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        note TEXT NOT NULL
    )
""")
notes_conn.commit()

new_note = st.text_area("Add a note:", placeholder="e.g. Wrist strain starting today. Skipping hang cleans for 2 weeks.")
if st.button("Save Note"):
    if new_note.strip():
        notes_conn.execute("INSERT INTO athlete_notes (note) VALUES (?)", (new_note.strip(),))
        notes_conn.commit()
        st.success("Note saved!")
        st.rerun()
    else:
        st.warning("Note is empty.")

notes = pd.read_sql_query("SELECT created_at, note FROM athlete_notes ORDER BY created_at DESC", notes_conn)
notes_conn.close()

if not notes.empty:
    for _, row in notes.iterrows():
        st.markdown(f"**{row['created_at'][:10]}** — {row['note']}")
else:
    st.caption("No notes yet.")

conn.close()

# ── AI Coach Chat ─────────────────────────────────────────────
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
            history = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages[:-1]
            ]
            response = ask_atlas(prompt, chat_history=history)
            st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})