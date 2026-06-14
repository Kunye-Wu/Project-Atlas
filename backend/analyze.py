import sqlite3
import pandas as pd

conn = sqlite3.connect('data/atlas.db')

# ── 1. Squat progression (heaviest set per workout day) ──────────────────
print("=== SQUAT PROGRESSION ===")
squat = pd.read_sql_query("""
    SELECT substr(start_time, 1, 10) as date, MAX(weight_lbs) as max_weight, MAX(reps) as reps_at_max
    FROM sets
    WHERE exercise_title = 'Squat (Barbell)'
    AND set_type = 'normal'
    AND weight_lbs > 0
    GROUP BY substr(start_time, 1, 10)
    ORDER BY date
""", conn)
print(squat.to_string(index=False))

# ── 2. Bench Press progression ───────────────────────────────────────────
print("\n=== BENCH PRESS PROGRESSION ===")
bench = pd.read_sql_query("""
    SELECT substr(start_time, 1, 10) as date, MAX(weight_lbs) as max_weight, MAX(reps) as reps_at_max
    FROM sets
    WHERE exercise_title = 'Bench Press (Barbell)'
    AND set_type = 'normal'
    AND weight_lbs > 0
    GROUP BY substr(start_time, 1, 10)
    ORDER BY date
""", conn)
print(bench.to_string(index=False))

# ── 3. Top 5 heaviest lifts ever ─────────────────────────────────────────
print("\n=== TOP 10 HEAVIEST SETS EVER ===")
top = pd.read_sql_query("""
    SELECT substr(start_time, 1, 10) as date, exercise_title, weight_lbs, reps, set_type
    FROM sets
    WHERE set_type = 'normal'
    AND weight_lbs > 0
    ORDER BY weight_lbs DESC
    LIMIT 10
""", conn)
print(top.to_string(index=False))

# ── 4. Weekly volume per workout type ────────────────────────────────────
print("\n=== WEEKLY TRAINING VOLUME (total sets per week) ===")
volume = pd.read_sql_query("""
    SELECT strftime('%Y-W%W', start_time) as week, title, COUNT(*) as total_sets
    FROM sets
    WHERE set_type = 'normal'
    GROUP BY week, title
    ORDER BY week DESC
    LIMIT 20
""", conn)
print(volume.to_string(index=False))

conn.close()