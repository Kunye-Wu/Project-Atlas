# 🏋️ Project Atlas

> **Atlas is an AI-powered strength coaching platform that interprets your training data — not just tracks it.**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)](https://project-atlas-8vwappjmulurmuarlbfbgcc.streamlit.app) 
[![Python](https://img.shields.io/badge/Python-3.9-3776AB?style=for-the-badge&logo=python)](https://python.org)
[![Claude API](https://img.shields.io/badge/AI-Claude%20API-black?style=for-the-badge)](https://anthropic.com)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?style=for-the-badge&logo=sqlite)](https://sqlite.org)

---

## What Atlas Does

Most fitness apps track your workouts. Atlas interprets them.

Atlas analyzes years of real training data, detects plateaus before you notice them, remembers context you've logged (injuries, life stress, sleep), and delivers personalized coaching — not generic advice.

**Ask Atlas:**
- *"Why has my squat been stalled for the past month?"*
- *"How ready am I for a PR attempt this week?"*
- *"Am I accumulating too much fatigue to hit my goals?"*
- *"What should my next training block look like?"*

Atlas answers with your actual data, your actual history, and your actual context.

---

## Features

### 🔄 Live Data Sync
Upload your latest Hevy CSV export and Atlas rebuilds its database instantly — no terminal required.

### 📋 Weekly Check-in
Atlas proactively summarizes your week without being asked: training volume, lift trends, flags, and a specific recommendation for next week.

### 🔍 Plateau Detection
Custom Epley e1RM trend analysis across 12 tracked lifts. Flags any lift with less than 3% improvement over the last 4 sessions — with green/red visual cards on the dashboard.

### 📈 Exercise Progression Charts
Interactive Plotly charts for any exercise in your database, with gold star markers on every PR date and hover tooltips showing exact weight and date.

### 📝 Athlete Notes
Log context Atlas can't see in the data — injuries, deloads, life factors. Atlas reads these notes and incorporates them into every coaching response, distinguishing real plateaus from recovery artifacts.

### 🤖 Conversational AI Coach
Full conversation memory within a session. Ask follow-up questions, provide context, and Atlas updates its reasoning — not just its answer.

---

## Architecture 

Project-Atlas/
├── ai/
│   └── coach.py              # Claude API integration, weekly check-in
├── backend/
│   ├── build_database.py     # CSV → SQLite pipeline
│   ├── plateau_detector.py   # Epley e1RM trend analysis
│   └── load_data.py          # Data overview utility
├── frontend/
│   └── dashboard.py          # Streamlit dashboard
├── data/
│   ├── atlas.db              # SQLite database
│   └── workout_data.csv      # Hevy export
├── vision.md
├── roadmap.md
└── journal.md

---

## Running Locally

```bash
git clone https://github.com/Kunye-Wu/Project-Atlas.git
cd Project-Atlas
pip install -r requirements.txt

# Add your Anthropic API key
echo "ANTHROPIC_API_KEY=your_key_here" > .env

# Build the database
python3 backend/build_database.py

# Launch the dashboard
python3 -m streamlit run frontend/dashboard.py
```

---

## Data

Built on 4,100+ real sets logged from September 2025 through present — squats, bench, deadlifts, overhead press, accessory work, and more. Atlas's coaching is grounded in longitudinal training history, not synthetic data.

---

## Development Journal

This project was built session by session over summer 2026, with every decision, bug, and milestone logged in [`journal.md`](journal.md). The journal documents the full engineering process — not just the final result.

---

## About

Built by [Kevin (Kunye) Wu](https://github.com/Kunye-Wu) — Reed College, Mathematics.  
Summer 2026 independent project.

> *"I didn't want to build another fitness tracker. I wanted to build the coach that every tracker is missing."*