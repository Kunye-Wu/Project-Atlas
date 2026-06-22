import sqlite3
import pandas as pd

def detect_plateaus(min_sessions=4, threshold_pct=3.0):
    """
    For each major lift, calculate estimated 1RM trend over recent sessions.
    Flag as plateau if improvement is less than threshold_pct over min_sessions.
    Epley formula for estimated 1RM: weight * (1 + reps/30)
    """
    conn = sqlite3.connect('data/atlas.db')

    major_lifts = [
    'Squat (Barbell)',
    'Bench Press (Barbell)',
    'Deadlift (Trap bar)',
    'Overhead Press (Barbell)',
    'Push Press',
    'Pull Up',
    'Pull Up (Weighted)',
    'Chin Up',
    'Chin Up (Weighted)',
    'Incline Bench Press (Dumbbell)',
    'Hang Clean',
    'Lat Pulldown (Cable)',
]

    results = {}

    for lift in major_lifts:
        df = pd.read_sql_query(f"""
            SELECT start_time, weight_lbs, reps
            FROM sets
            WHERE exercise_title = '{lift}'
            AND set_type = 'normal'
            AND weight_lbs > 0
            AND reps > 0
            ORDER BY start_time
        """, conn)

        if len(df) < min_sessions:
            continue

        # Calculate estimated 1RM using Epley formula
        df['e1rm'] = df['weight_lbs'] * (1 + df['reps'] / 30)

        # Group by session date — take best e1RM per session
        df['date'] = pd.to_datetime(df['start_time'], errors='coerce')
        df = df.dropna(subset=['date'])
        df['date'] = df['date'].dt.date

        sessions = df.groupby('date')['e1rm'].max().reset_index()
        sessions = sessions.sort_values('date').tail(min_sessions)

        if len(sessions) < min_sessions:
            continue

        first_e1rm = sessions.iloc[0]['e1rm']
        last_e1rm = sessions.iloc[-1]['e1rm']
        pct_change = ((last_e1rm - first_e1rm) / first_e1rm) * 100

        first_date = sessions.iloc[0]['date']
        last_date = sessions.iloc[-1]['date']

        results[lift] = {
            'first_e1rm': round(first_e1rm, 1),
            'last_e1rm': round(last_e1rm, 1),
            'pct_change': round(pct_change, 1),
            'sessions_analyzed': len(sessions),
            'first_date': str(first_date),
            'last_date': str(last_date),
            'plateau': pct_change < threshold_pct
        }

    conn.close()
    return results

if __name__ == "__main__":
    print("=== ATLAS PLATEAU DETECTION ===\n")
    results = detect_plateaus()

    for lift, data in results.items():
        status = "⚠️  PLATEAU DETECTED" if data['plateau'] else "✅ PROGRESSING"
        print(f"{lift}")
        print(f"  Status: {status}")
        print(f"  Estimated 1RM: {data['first_e1rm']} → {data['last_e1rm']} lbs")
        print(f"  Change: {data['pct_change']:+.1f}% over {data['sessions_analyzed']} sessions")
        print(f"  Period: {data['first_date']} → {data['last_date']}")
        print()