import pandas as pd
import sqlite3

# Load raw CSV
df = pd.read_csv('data/workout_data.csv')

# Convert start_time to proper ISO format so SQLite can sort/filter correctly
df['start_time'] = pd.to_datetime(df['start_time'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')

# Connect to (or create) the database
conn = sqlite3.connect('data/atlas.db')

# Write the data to a table called 'sets'
df.to_sql('sets', conn, if_exists='replace', index=False)

print("=== DATABASE BUILT ===")
print(f"Table 'sets' created with {len(df)} rows")

# Test a query — all unique workouts
cursor = conn.cursor()
cursor.execute("SELECT DISTINCT title FROM sets ORDER BY title")
workouts = cursor.fetchall()
print(f"\nWorkouts in database:")
for w in workouts:
    print(f" - {w[0]}")

conn.close()
print("\nAtlas database ready.")