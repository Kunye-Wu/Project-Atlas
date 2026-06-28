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

    return lift_history_text, prs.to_string(index=False), recent_volume.to_string(index=False), plateau_summary, athlete_notes_text


def ask_atlas(question, chat_history=None):
    """Send a question to Claude with training data as context."""
    if chat_history is None:
        chat_history = []

    lift_histories, pr_data, volume_data, plateau_summary, athlete_notes_text = get_training_summary()

    system_prompt = f"""You are Atlas, an intelligent fitness coach analyzing real training data for Kevin, a serious lifter.

Here are Kevin's personal records (top lifts by weight):
{pr_data}

Here is Kevin's training volume by workout type (all-time, total sets and sessions):
{volume_data}

Here is the current plateau status for Kevin's tracked lifts (based on estimated 1RM trend over last 4 sessions):
{plateau_summary}

Here are Kevin's athlete notes — personal context he's logged that the data can't capture (injuries, life factors, subjective feelings):
{athlete_notes_text}

Here is Kevin's complete training history for his major lifts:
{lift_histories}

Answer Kevin's question as a knowledgeable, direct strength coach would. Reference specific numbers and dates from his actual data when relevant. Be concise but insightful. Avoid generic fitness advice — ground everything in his real training history. When relevant, proactively reference the plateau status of specific lifts. If athlete notes are relevant to the question, reference them explicitly."""

    messages = chat_history + [{"role": "user", "content": question}]

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system=system_prompt,
        messages=messages
    )

    return message.content[0].text


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