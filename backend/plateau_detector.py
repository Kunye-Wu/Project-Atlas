import sqlite3
import pandas as pd

RECENT_WEEKS = 12
MIN_RECENT_SESSIONS = 6
MAX_TRACKED_LIFTS = 9  # fills the dashboard's 3-column grid evenly

# Always tracked (ahead of everything else) when they meet the session minimum.
MAIN_LIFTS = [
    'Squat (Barbell)',
    'Bench Press (Barbell)',
    'Overhead Press (Barbell)',
    'Deadlift (Trap bar)',
    'Hang Clean',
]

# How each metric is measured. Bodyweight sets are logged with an empty or 0 weight.
METRICS = {
    'e1rm': {'label': 'e1RM', 'unit': 'lbs', 'weight_filter': 'weight_lbs > 0'},
    'reps': {'label': 'Best reps', 'unit': 'reps', 'weight_filter': 'COALESCE(weight_lbs, 0) = 0'},
}


def select_tracked_lifts(conn, weeks=RECENT_WEEKS,
                         min_sessions=MIN_RECENT_SESSIONS,
                         max_lifts=MAX_TRACKED_LIFTS):
    """
    Pick which lifts to track, returned as a list of (exercise, metric).

    "Recent" is the `weeks` weeks ending at the latest workout in the data
    (not today's date), so an old export still yields sensible lifts.
    A session is a distinct training day with at least one working set of reps.

    An exercise is tracked by e1RM if it has `min_sessions` weighted sessions,
    otherwise by best reps if it has `min_sessions` bodyweight sessions.
    MAIN_LIFTS that qualify come first; remaining slots go to other qualifying
    exercises ranked by session count (ties broken by name), up to max_lifts.
    """
    counts = pd.read_sql_query(f"""
        SELECT exercise_title,
               COUNT(DISTINCT CASE WHEN {METRICS['e1rm']['weight_filter']}
                     THEN date(start_time) END) AS weighted_sessions,
               COUNT(DISTINCT CASE WHEN {METRICS['reps']['weight_filter']}
                     THEN date(start_time) END) AS bodyweight_sessions
        FROM sets
        WHERE set_type = 'normal'
          AND reps > 0
          AND date(start_time) > (SELECT date(MAX(start_time), ?) FROM sets)
        GROUP BY exercise_title
    """, conn, params=(f'-{weeks * 7} days',))

    candidates = {}  # exercise -> (metric, sessions)
    for row in counts.itertuples(index=False):
        if row.weighted_sessions >= min_sessions:
            candidates[row.exercise_title] = ('e1rm', row.weighted_sessions)
        elif row.bodyweight_sessions >= min_sessions:
            candidates[row.exercise_title] = ('reps', row.bodyweight_sessions)

    main = [lift for lift in MAIN_LIFTS if lift in candidates]
    others = sorted((lift for lift in candidates if lift not in main),
                    key=lambda lift: (-candidates[lift][1], lift))
    return [(lift, candidates[lift][0]) for lift in (main + others)[:max_lifts]]


def detect_plateaus(min_sessions=4, threshold_pct=3.0):
    """
    For each tracked lift, calculate the trend of its metric over recent sessions:
    estimated 1RM for weighted lifts, best reps per session for bodyweight lifts.
    Flag as plateau if improvement is less than threshold_pct over min_sessions.
    Epley formula for estimated 1RM: weight * (1 + reps/30)
    """
    conn = sqlite3.connect('data/atlas.db')

    results = {}

    for lift, metric in select_tracked_lifts(conn):
        spec = METRICS[metric]
        df = pd.read_sql_query(f"""
            SELECT start_time, weight_lbs, reps
            FROM sets
            WHERE exercise_title = ?
            AND set_type = 'normal'
            AND {spec['weight_filter']}
            AND reps > 0
            ORDER BY start_time
        """, conn, params=(lift,))

        if len(df) < min_sessions:
            continue

        if metric == 'e1rm':
            df['value'] = df['weight_lbs'] * (1 + df['reps'] / 30)
        else:
            df['value'] = df['reps']

        # Group by session date — take the best value per session
        df['date'] = pd.to_datetime(df['start_time'], errors='coerce')
        df = df.dropna(subset=['date'])
        df['date'] = df['date'].dt.date

        sessions = df.groupby('date')['value'].max().reset_index()
        sessions = sessions.sort_values('date').tail(min_sessions)

        if len(sessions) < min_sessions:
            continue

        first_value = sessions.iloc[0]['value']
        last_value = sessions.iloc[-1]['value']
        pct_change = ((last_value - first_value) / first_value) * 100

        results[lift] = {
            'metric': metric,
            'label': spec['label'],
            'unit': spec['unit'],
            'first_value': round(first_value, 1) if metric == 'e1rm' else int(first_value),
            'last_value': round(last_value, 1) if metric == 'e1rm' else int(last_value),
            'pct_change': round(pct_change, 1),
            'sessions_analyzed': len(sessions),
            'first_date': str(sessions.iloc[0]['date']),
            'last_date': str(sessions.iloc[-1]['date']),
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
        print(f"  {data['label']}: {data['first_value']} → {data['last_value']} {data['unit']}")
        print(f"  Change: {data['pct_change']:+.1f}% over {data['sessions_analyzed']} sessions")
        print(f"  Period: {data['first_date']} → {data['last_date']}")
        print()
