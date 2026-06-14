import pandas as pd

# Load the raw Hevy export
df = pd.read_csv('data/workout_data.csv')

# Basic overview
print("=== ATLAS DATA OVERVIEW ===")
print(f"Total rows: {len(df)}")
print(f"Columns: {list(df.columns)}")
print(f"\nDate range: {df['start_time'].min()} → {df['start_time'].max()}")
print(f"Total workouts: {df['title'].nunique()}")
print(f"Unique exercises: {df['exercise_title'].nunique()}")
print(f"\nWorkout types:")
print(df['title'].value_counts().head(10))