import os
import sqlite3
import pandas as pd
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def get_training_summary():
    """Pull a summary of recent training data to give Claude context."""
    conn = sqlite3.connect('data/atlas.db')

    recent = pd.read_sql_query("""
        SELECT start_time, title, exercise_title, weight_lbs, reps, set_type
        FROM sets
        WHERE set_type = 'normal'
        AND weight_lbs > 0
        ORDER BY start_time DESC
        LIMIT 100
    """, conn)

    prs = pd.read_sql_query("""
        SELECT exercise_title, MAX(weight_lbs) as max_weight
        FROM sets
        WHERE set_type = 'normal'
        AND weight_lbs > 0
        GROUP BY exercise_title
        ORDER BY max_weight DESC
        LIMIT 15
    """, conn)

    conn.close()
    return recent.to_string(index=False), prs.to_string(index=False)

def ask_atlas(question):
    """Send a question to Claude with training data as context."""
    recent_data, pr_data = get_training_summary()

    system_prompt = f"""You are Atlas, an intelligent fitness coach analyzing real training data for Kevin, a serious lifter.

Here are Kevin's personal records (top lifts by weight):
{pr_data}

Here is Kevin's last 100 sets logged:
{recent_data}

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