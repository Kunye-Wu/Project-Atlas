import os
import sqlite3
import pandas as pd
from anthropic import Anthropic
from dotenv import load_dotenv
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.plateau_detector import detect_plateaus

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def _finish(message):
    """Return the reply text; if it hit the length cap, end it cleanly instead of mid-sentence."""
    text = message.content[0].text
    if message.stop_reason == "max_tokens":
        cut = max(text.rfind(". "), text.rfind(".\n"), text.rfind("\n\n"))
        if cut > 0:
            text = text[:cut + 1]
        if text.count("**") % 2:
            text += "**"
        text += "\n\n_(Answer shortened — ask a follow-up for more detail.)_"
    return text

def get_training_summary():
    """Pull comprehensive training data — full history per major lift, plus recent overall activity."""
    conn = sqlite3.connect('data/atlas.db')

    major_lifts = ['Squat (Barbell)', 'Bench Press (Barbell)', 'Deadlift (Trap bar)', 'Overhead Press (Barbell)']
    lift_histories = {}
    for lift in major_lifts:
        history = pd.read_sql_query(f"""
            SELECT start_time, weight_lbs, reps, set_type
            FROM sets
            WHERE exercise_title = '{lift}'
            AND set_type = 'normal'
            AND weight_lbs > 0
            ORDER BY start_time
        """, conn)
        if not history.empty:
            lift_histories[lift] = history.to_string(index=False)

    prs = pd.read_sql_query("""
        SELECT exercise_title, MAX(weight_lbs) as max_weight
        FROM sets
        WHERE set_type = 'normal'
        AND weight_lbs > 0
        GROUP BY exercise_title
        ORDER BY max_weight DESC
        LIMIT 15
    """, conn)

    recent_volume = pd.read_sql_query("""
        SELECT title, COUNT(*) as total_sets, COUNT(DISTINCT date(start_time)) as sessions
        FROM sets
        WHERE set_type = 'normal'
        GROUP BY title
        ORDER BY total_sets DESC
    """, conn)

    conn.close()

    # Build plateau summary string
    plateau_data = detect_plateaus()
    plateau_lines = []
    for lift, data in plateau_data.items():
        status = "⚠️ PLATEAU" if data['plateau'] else "✅ PROGRESSING"
        plateau_lines.append(
            f"  {lift}: {status} | e1RM {data['first_e1rm']} → {data['last_e1rm']} lbs "
            f"({data['pct_change']:+.1f}% over {data['sessions_analyzed']} sessions, "
            f"{data['first_date']} → {data['last_date']})"
        )
    plateau_summary = "\n".join(plateau_lines)

    lift_history_text = "\n\n".join([f"=== {lift} full history ===\n{hist}" for lift, hist in lift_histories.items()])

    # Fetch athlete notes
    notes_conn = sqlite3.connect('data/atlas.db')
    notes_df = pd.read_sql_query("""
        SELECT created_at, note
        FROM athlete_notes
        ORDER BY created_at DESC
    """, notes_conn)
    notes_conn.close()

    if not notes_df.empty:
        notes_lines = [f"  [{row['created_at'][:10]}] {row['note']}" for _, row in notes_df.iterrows()]
        athlete_notes_text = "\n".join(notes_lines)
    else:
        athlete_notes_text = "No notes logged yet."

    # Fetch goals
    try:
        goals_conn = sqlite3.connect('data/atlas.db')
        goals_df = pd.read_sql_query("""
            SELECT exercise, target_weight FROM goals ORDER BY created_at DESC
        """, goals_conn)
        goals_conn.close()

        if not goals_df.empty:
            goal_lines = []
            pr_conn = sqlite3.connect('data/atlas.db')
            for _, goal in goals_df.iterrows():
                exercise = goal['exercise']
                target = goal['target_weight']
                pr_result = pd.read_sql_query(f"""
                    SELECT MAX(weight_lbs) as pr FROM sets
                    WHERE exercise_title = '{exercise}'
                    AND set_type = 'normal' AND weight_lbs > 0
                """, pr_conn)
                current_pr = pr_result['pr'].iloc[0] if not pr_result.empty else 0
                if current_pr:
                    pct = (current_pr / target) * 100
                    lbs_remaining = max(target - current_pr, 0)
                    if lbs_remaining == 0:
                        goal_lines.append(f"  {exercise}: Goal {target} lbs — REACHED ✅")
                    else:
                        goal_lines.append(f"  {exercise}: Goal {target} lbs — Current PR {current_pr} lbs ({pct:.1f}% complete, {lbs_remaining} lbs remaining)")
            pr_conn.close()
            goals_text = "\n".join(goal_lines)
        else:
            goals_text = "No goals set yet."
    except Exception:
        goals_text = "No goals set yet."

    return lift_history_text, prs.to_string(index=False), recent_volume.to_string(index=False), plateau_summary, athlete_notes_text, goals_text


def get_weekly_checkin():
    """Generate a proactive weekly check-in summary based on last 7 days of training."""
    conn = sqlite3.connect('data/atlas.db')

    # Last 7 days of training
    recent_sets = pd.read_sql_query("""
        SELECT exercise_title, start_time, weight_lbs, reps, title as workout_type
        FROM sets
        WHERE set_type = 'normal'
        AND weight_lbs > 0
        AND date(start_time) >= date('now', '-7 days')
        ORDER BY start_time
    """, conn)

    # Prior 7 days for comparison
    prior_sets = pd.read_sql_query("""
        SELECT exercise_title, start_time, weight_lbs, reps
        FROM sets
        WHERE set_type = 'normal'
        AND weight_lbs > 0
        AND date(start_time) >= date('now', '-14 days')
        AND date(start_time) < date('now', '-7 days')
        ORDER BY start_time
    """, conn)

    # All-time PRs for context
    prs = pd.read_sql_query("""
        SELECT exercise_title, MAX(weight_lbs) as max_weight
        FROM sets
        WHERE set_type = 'normal' AND weight_lbs > 0
        GROUP BY exercise_title
        ORDER BY max_weight DESC
        LIMIT 15
    """, conn)

    conn.close()

    # Fetch recent athlete notes (last 14 days)
    notes_conn = sqlite3.connect('data/atlas.db')
    recent_notes_df = pd.read_sql_query("""
        SELECT created_at, note
        FROM athlete_notes
        WHERE date(created_at) >= date('now', '-14 days')
        ORDER BY created_at DESC
    """, notes_conn)
    notes_conn.close()

    # Build recent week summary
    if recent_sets.empty:
        recent_summary = "No workouts logged in the last 7 days."
    else:
        workouts_this_week = recent_sets['start_time'].apply(lambda x: x[:10]).nunique()
        sets_this_week = len(recent_sets)
        exercises_this_week = recent_sets['exercise_title'].nunique()

        major_lifts = ['Squat (Barbell)', 'Bench Press (Barbell)', 'Deadlift (Trap bar)', 'Overhead Press (Barbell)']
        lift_comparisons = []
        for lift in major_lifts:
            recent_lift = recent_sets[recent_sets['exercise_title'] == lift].copy()
            prior_lift = prior_sets[prior_sets['exercise_title'] == lift].copy()

            if not recent_lift.empty:
                recent_lift['e1rm'] = recent_lift['weight_lbs'] * (1 + recent_lift['reps'] / 30)
                best_recent = recent_lift['e1rm'].max()

                if not prior_lift.empty:
                    prior_lift['e1rm'] = prior_lift['weight_lbs'] * (1 + prior_lift['reps'] / 30)
                    best_prior = prior_lift['e1rm'].max()
                    pct_change = ((best_recent - best_prior) / best_prior) * 100
                    lift_comparisons.append(f"  {lift}: e1RM {best_recent:.1f} lbs ({pct_change:+.1f}% vs prior week)")
                else:
                    lift_comparisons.append(f"  {lift}: e1RM {best_recent:.1f} lbs (no prior week data)")

        lift_summary = "\n".join(lift_comparisons) if lift_comparisons else "None of the major lifts trained this week."

        recent_summary = f"""Workouts this week: {workouts_this_week}
Total sets: {sets_this_week}
Exercises trained: {exercises_this_week}

Major lift e1RM this week vs prior week:
{lift_summary}"""

    if not recent_notes_df.empty:
        notes_text = "\n".join([f"  [{row['created_at'][:10]}] {row['note']}" for _, row in recent_notes_df.iterrows()])
    else:
        notes_text = "No notes logged in the last 14 days."

    plateau_data = detect_plateaus()
    plateau_lines = []
    for lift, data in plateau_data.items():
        status = "⚠️ PLATEAU" if data['plateau'] else "✅ PROGRESSING"
        plateau_lines.append(f"  {lift}: {status} ({data['pct_change']:+.1f}%)")
    plateau_text = "\n".join(plateau_lines)

    system_prompt = """You are Atlas, an intelligent fitness coach. Generate a concise, proactive weekly check-in summary for Kevin. 
Be direct and specific — reference actual numbers. Structure it clearly with these sections:
1. This Week's Training (what was done)
2. Key Lifts (how the major lifts moved)
3. Flags (anything to watch — plateaus, missing lifts, fatigue signs)
4. Recommendation (one clear action for next week)

Keep the total response under 300 words. Use bold for section headers."""

    user_prompt = f"""Here is Kevin's training data for the weekly check-in:

LAST 7 DAYS:
{recent_summary}

PLATEAU STATUS:
{plateau_text}

RECENT ATHLETE NOTES (last 14 days):
{notes_text}

ALL-TIME PRs:
{prs.to_string(index=False)}

Generate Kevin's weekly check-in."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )

    return _finish(message)


def ask_atlas(question, chat_history=None):
    """Send a question to Claude with training data as context."""
    if chat_history is None:
        chat_history = []

    lift_histories, pr_data, volume_data, plateau_summary, athlete_notes_text, goals_text = get_training_summary()

    system_prompt = f"""You are Atlas, an intelligent fitness coach analyzing real training data for Kevin, a serious lifter.

Here are Kevin's personal records (top lifts by weight):
{pr_data}

Here is Kevin's training volume by workout type (all-time, total sets and sessions):
{volume_data}

Here is the current plateau status for Kevin's tracked lifts (based on estimated 1RM trend over last 4 sessions):
{plateau_summary}

Here are Kevin's athlete notes — personal context he's logged that the data can't capture (injuries, life factors, subjective feelings):
{athlete_notes_text}

Here are Kevin's current training goals:
{goals_text}

Here is Kevin's complete training history for his major lifts:
{lift_histories}

Answer Kevin's question as a knowledgeable, direct strength coach would. Reference specific numbers and dates from his actual data when relevant. Be concise but insightful. Avoid generic fitness advice — ground everything in his real training history. When relevant, proactively reference the plateau status of specific lifts. If athlete notes are relevant to the question, reference them explicitly. When discussing a lift that has a goal set, reference the goal and how current progress relates to it."""

    messages = chat_history + [{"role": "user", "content": question}]

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system=system_prompt,
        messages=messages
    )

    return _finish(message)


if __name__ == "__main__":
    print("=== ATLAS AI COACH ===")
    print("Ask Atlas a question about your training (or 'quit' to exit)\n")

    while True:
        question = input("You: ")
        if question.lower() == 'quit':
            break
        print("\nAtlas: ", end="")
        answer = ask_atlas(question)
        print(answer)
        print()