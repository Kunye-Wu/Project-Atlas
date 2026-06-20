import os
import sqlite3
import pandas as pd
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def get_training_summary():
    """Pull comprehensive training data — full history per major lift, plus recent overall activity."""
    conn = sqlite3.connect('data/atlas.db')

    # Full history for major lifts — not just recent rows
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

    # All-time PRs
    prs = pd.read_sql_query("""
        SELECT exercise_title, MAX(weight_lbs) as max_weight
        FROM sets
        WHERE set_type = 'normal'
        AND weight_lbs > 0
        GROUP BY exercise_title
        ORDER BY max_weight DESC
        LIMIT 15
    """, conn)

    # Last 90 days of activity, summarized by workout type
    recent_volume = pd.read_sql_query("""
        SELECT title, COUNT(*) as total_sets, COUNT(DISTINCT date(start_time)) as sessions
        FROM sets
        WHERE set_type = 'normal'
        GROUP BY title
        ORDER BY total_sets DESC
    """, conn)

    conn.close()

    lift_history_text = "\n\n".join([f"=== {lift} full history ===\n{hist}" for lift, hist in lift_histories.items()])

    return lift_history_text, prs.to_string(index=False), recent_volume.to_string(index=False)

def ask_atlas(question):
    """Send a question to Claude with training data as context."""
    lift_histories, pr_data, volume_data = get_training_summary()

    system_prompt = f"""You are Atlas, an intelligent fitness coach analyzing real training data for Kevin, a serious lifter.

Here are Kevin's personal records (top lifts by weight):
{pr_data}

Here is Kevin's training volume by workout type (all-time, total sets and sessions):
{volume_data}

Here is Kevin's complete training history for his major lifts:
{lift_histories}

Answer Kevin's question as a knowledgeable, direct strength coach would. Reference specific numbers and dates from his actual data when relevant. Be concise but insightful. Avoid generic fitness advice — ground everything in his real training history."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system=system_prompt,
        messages=[{"role": "user", "content": question}]
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