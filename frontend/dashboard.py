import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import sys
import os
from datetime import datetime, timedelta
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from ai.coach import ask_atlas, get_weekly_checkin
from backend.plateau_detector import detect_plateaus

st.set_page_config(page_title="Project Atlas", page_icon="🏋️", layout="wide")

conn = sqlite3.connect('data/atlas.db')

# ── Header ────────────────────────────────────────────────────
st.title("🏋️ Project Atlas")
st.subheader("Your Personal Training Intelligence Dashboard")

# ── CSV Re-upload ──────────────────────────────────────────────
st.subheader("🔄 Update Training Data")
st.caption("Export your latest workouts from Hevy and upload the CSV to refresh Atlas.")

uploaded_file = st.file_uploader("Upload Hevy CSV export", type="csv")

if uploaded_file is not None:
    new_df = pd.read_csv(uploaded_file)

    required_columns = {'title', 'start_time', 'exercise_title', 'set_type', 'weight_lbs', 'reps'}
    missing = required_columns - set(new_df.columns)

    if missing:
        st.error(f"This CSV is missing required columns: {', '.join(missing)}. Upload a valid Hevy export.")
    else:
        if st.button("Confirm and Rebuild Database"):
            new_df['start_time'] = pd.to_datetime(new_df['start_time'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')
            new_df.to_csv('data/workout_data.csv', index=False)
            rebuild_conn = sqlite3.connect('data/atlas.db')
            new_df.to_sql('sets', rebuild_conn, if_exists='replace', index=False)
            rebuild_conn.close()
            latest_date = pd.to_datetime(new_df['start_time'], errors='coerce').max()
            st.success(f"Database updated! {len(new_df):,} sets loaded. Latest workout: {latest_date.strftime('%B %d, %Y')}")
            st.rerun()

st.divider()

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

# ── Weekly Check-in ───────────────────────────────────────────
st.subheader("📋 Weekly Check-in")
st.caption("Atlas proactively summarizes your last 7 days of training.")

if "weekly_checkin" not in st.session_state:
    st.session_state.weekly_checkin = None

col_btn1, col_btn2 = st.columns([1, 5])
with col_btn1:
    if st.button("Generate Check-in"):
        with st.spinner("Atlas is reviewing your week..."):
            st.session_state.weekly_checkin = get_weekly_checkin()

if st.session_state.weekly_checkin:
    st.markdown(st.session_state.weekly_checkin)
    with col_btn2:
        st.download_button(
            label="⬇ Export as .txt",
            data=st.session_state.weekly_checkin,
            file_name="atlas_weekly_checkin.txt",
            mime="text/plain"
        )

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

# ── Goal Tracking ─────────────────────────────────────────────
st.subheader("🎯 Goal Tracking")
st.caption("Set a target and Atlas will estimate when you'll get there based on your rate of progress.")

# Create goals table if it doesn't exist
goals_conn = sqlite3.connect('data/atlas.db')
goals_conn.execute("""
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exercise TEXT NOT NULL,
        target_weight REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
goals_conn.commit()

# Add new goal
all_exercises_for_goals = pd.read_sql_query("""
    SELECT DISTINCT exercise_title FROM sets
    WHERE set_type = 'normal' AND weight_lbs > 0
    ORDER BY exercise_title
""", conn)
exercise_options = all_exercises_for_goals['exercise_title'].tolist()

col_g1, col_g2, col_g3 = st.columns([3, 2, 1])
with col_g1:
    goal_exercise = st.selectbox("Exercise", exercise_options,
        index=exercise_options.index('Squat (Barbell)') if 'Squat (Barbell)' in exercise_options else 0,
        key="goal_exercise_select")
with col_g2:
    goal_target = st.number_input("Target weight (lbs)", min_value=1, max_value=2000, value=450, step=5)
with col_g3:
    st.write("")
    st.write("")
    if st.button("Set Goal"):
        # Remove existing goal for same exercise before adding new one
        goals_conn.execute("DELETE FROM goals WHERE exercise = ?", (goal_exercise,))
        goals_conn.execute("INSERT INTO goals (exercise, target_weight) VALUES (?, ?)",
            (goal_exercise, goal_target))
        goals_conn.commit()
        st.success(f"Goal set: {goal_exercise} → {goal_target} lbs")
        st.rerun()

# Display existing goals with progress
goals = pd.read_sql_query("SELECT * FROM goals ORDER BY created_at DESC", goals_conn)
goals_conn.close()

if not goals.empty:
    for _, goal in goals.iterrows():
        exercise = goal['exercise']
        target = goal['target_weight']

        # Get current PR for this exercise
        pr_result = pd.read_sql_query(f"""
            SELECT MAX(weight_lbs) as pr
            FROM sets
            WHERE exercise_title = '{exercise}'
            AND set_type = 'normal' AND weight_lbs > 0
        """, conn)
        current_pr = pr_result['pr'].iloc[0] if not pr_result.empty else 0

        if current_pr is None:
            continue

        pct_complete = min((current_pr / target) * 100, 100)
        lbs_remaining = max(target - current_pr, 0)

        # Estimate rate of progress — lbs gained per week from PR history
        pr_history = pd.read_sql_query(f"""
            SELECT date(start_time) as date, MAX(weight_lbs) as max_weight
            FROM sets
            WHERE exercise_title = '{exercise}'
            AND set_type = 'normal' AND weight_lbs > 0
            GROUP BY date(start_time)
            ORDER BY date
        """, conn)

        eta_str = "Unknown"
        weekly_rate = None
        if len(pr_history) >= 4:
            pr_history['date'] = pd.to_datetime(pr_history['date'])
            pr_history['running_max'] = pr_history['max_weight'].cummax()
            first_pr = pr_history['running_max'].iloc[0]
            last_pr = pr_history['running_max'].iloc[-1]
            first_date = pr_history['date'].iloc[0]
            last_date = pr_history['date'].iloc[-1]
            weeks_elapsed = max((last_date - first_date).days / 7, 1)
            weekly_rate = (last_pr - first_pr) / weeks_elapsed

            if weekly_rate > 0 and lbs_remaining > 0:
                weeks_to_goal = lbs_remaining / weekly_rate
                eta_date = datetime.now() + timedelta(weeks=weeks_to_goal)
                eta_str = eta_date.strftime("%B %Y")
            elif lbs_remaining == 0:
                eta_str = "Goal reached! 🎉"

        # Display goal card
        st.markdown(f"**{exercise}** — Target: {target} lbs")
        col_prog, col_stats = st.columns([3, 2])
        with col_prog:
            st.progress(pct_complete / 100)
        with col_stats:
            rate_str = f"{weekly_rate:.1f} lbs/week" if weekly_rate and weekly_rate > 0 else "Calculating..."
            st.markdown(f"**{current_pr} / {target} lbs** ({pct_complete:.1f}%) — "
                       f"{lbs_remaining} lbs to go · {rate_str} · ETA: **{eta_str}**")
        st.write("")
else:
    st.caption("No goals set yet. Add one above.")

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

exercise_data['prev_max'] = exercise_data['max_weight'].shift(1).fillna(0)
exercise_data['running_max'] = exercise_data['max_weight'].cummax()
exercise_data['is_pr'] = exercise_data['max_weight'] > exercise_data['prev_max'].cummax()
pr_points = exercise_data[exercise_data['is_pr']]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=exercise_data['date'],
    y=exercise_data['max_weight'],
    mode='lines',
    name='Max Weight',
    line=dict(color='#4C9BE8', width=2)
))
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

notes = pd.read_sql_query("SELECT id, created_at, note FROM athlete_notes ORDER BY created_at DESC", notes_conn)

if not notes.empty:
    for _, row in notes.iterrows():
        col_note, col_del = st.columns([10, 1])
        with col_note:
            st.markdown(f"**{row['created_at'][:10]}** — {row['note']}")
        with col_del:
            if st.button("🗑", key=f"del_{row['id']}"):
                notes_conn.execute("DELETE FROM athlete_notes WHERE id = ?", (row['id'],))
                notes_conn.commit()
                st.rerun()
else:
    st.caption("No notes yet.")

notes_conn.close()
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