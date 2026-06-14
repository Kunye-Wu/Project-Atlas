# Project Atlas — Claude Context File
Last updated: June 10, 2026

## Who I am
Kevin (Kunye Wu) — Reed College freshman, mathematics major.
Student-athlete, 3+ years of serious lifting.
Building Project Atlas over summer 2026 alongside internship searching.
GitHub: Kunye-Wu

## What Project Atlas is
An intelligent fitness agent that interprets training data, detects plateaus,
and coaches serious athletes — not a tracker, an interpreter.
Built on Kevin's personal Hevy workout data (3+ years of real lifting logs).

Target questions Atlas should answer:
- "How ready am I for a PR attempt this week?"
- "Why has my squat been stalled for the past month?"
- "Am I accumulating too much fatigue to hit my goals?"
- "What should my next training block look like?"

## Stack decided
- Frontend: Streamlit
- Backend: Python
- Database: SQLite (migrate to PostgreSQL later)
- AI layer: Claude API (primary), OpenAI API (secondary)
- Version control: GitHub (public)

## Project structure
Project-Atlas/
├── README.md
├── vision.md          ✅ written and pushed
├── requirements.md
├── roadmap.md
├── journal.md         ✅ started June 10
├── data/              (Hevy CSV export goes here)
├── backend/
├── frontend/
├── ai/
└── experiments/

## Progress log
### June 10 — Foundation Phase Complete
- Created full project folder structure on Mac (Desktop/Project-Atlas)
- Configured VS Code with shell command
- Created GitHub repo: github.com/Kunye-Wu/Project-Atlas
- Written and pushed vision.md (sharp, personal, specific)
- Started journal.md
- Two commits pushed successfully

## Next session goals (June 11)
- Export Hevy CSV and drop into data/ folder
- Design the data model (Phase II: giving Atlas a brain)
- Answer: what is a workout in Atlas? sets, reps, weights schema?
- First principles approach — no LangChain, no vector DBs yet

## Key decisions made
- Project name: Project-Atlas (not adaptive-lifting-ai)
- Starting with Kevin's own Hevy data as seed dataset
- Claude API preferred over OpenAI for conversational coaching layer
- SQLite first, PostgreSQL migration planned
- journal.md will log daily progress (move to journal/ folder later)

## How to use this file
Paste this at the start of every Claude session to restore full context.
Update the progress log and "next session goals" at the end of each session.

### June 13 — Phase II: Atlas Gets a Brain
- Exported Hevy workout data (3934 sets, Oct 2025 → Apr 2026)
- Built load_data.py — reads and summarizes raw CSV
- Built build_database.py — creates atlas.db (SQLite)
- Built analyze.py — first real training insights
- Confirmed PRs: Squat 420, Bench 335, Trap Bar Deadlift 455
- Squat peaked at 405 in March, slight dip since — worth investigating

## Next session goals
- Fix weekly volume date parsing (strftime issue)
- Build PR detection logic — find true 1RM dates
- Start Streamlit dashboard — make Atlas visual
- Begin plateau detection algorithm