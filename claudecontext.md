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

### June 14 — Phase III: Atlas Goes Visual
- Built frontend/dashboard.py with Streamlit
- Live dashboard at localhost:8501
- Squat + bench progression charts working with real dates
- Volume bar chart by workout type
- PR metric cards: 420 squat, 335 bench, 455 trap bar

## Next session goals
- Add AI coaching layer — ask Atlas questions about your training
- Add exercise selector dropdown (pick any lift to see its progression)
- Add plateau detection logic
- Begin Claude API integration for conversational coaching

### June 18 — Phase IV: Atlas Gets a Voice
- Got Claude API key, stored safely in .env (gitignored)
- Installed anthropic + python-dotenv libraries
- Built ai/coach.py — Atlas can now answer questions using Claude API
- Connected real training data (PRs + recent sets) as context for Claude
- First successful conversation: asked Atlas why squat stalled
- Atlas gave an honest, data-grounded answer — flagged data limitations,
  spotted squat absence in recent logs vs. chest-heavy sessions
- Confirmed: Atlas reasons intelligently, not just regurgitating stats

## Known issues to fix
- "Last 100 sets" window is too narrow/recency-biased — need time-based
  window instead (e.g. last 90 days) or per-exercise history pulls
- Raw Hevy export data may have inconsistencies worth auditing

## Next session goals
- Fix data window in coach.py (time-based, not row-count-based)
- Add per-exercise history fetching so Atlas can see full lift timelines
- Wire coach.py into the Streamlit dashboard — chat interface in browser
- Audit raw Hevy data for inconsistencies

### June 20 — Phase V: Atlas Becomes Fully Interactive
- Fixed coach.py data window — full per-exercise history instead of last 100 rows
- Confirmed fix works: Atlas now sees entire squat/bench timeline with real dates
- Wired ask_atlas() into frontend/dashboard.py via sys.path import
- Added Streamlit chat interface (st.chat_input + st.chat_message) at bottom of dashboard
- Atlas is now fully interactive in the browser — no terminal required
- Tested live: asked Atlas about bench progression (265→335 lbs claim)
- Atlas corrected the framing with exact dates, didn't just agree — genuine
  coaching behavior, not flattery
- Confirmed: closing terminal/Ctrl+C stops the local server safely
- Dashboard is currently local-only (localhost:8501) — not yet deployed publicly

## Next session goals
- Explore deploying to Streamlit Community Cloud for a public shareable URL
- Add exercise selector dropdown to charts
- Begin plateau detection algorithm (automated, not just chat-based)
- Consider adding a "weekly check-in" feature — Atlas proactively summarizes the week

### June 21 — Phase VI: Atlas Becomes Proactive
- Built backend/plateau_detector.py — Epley formula e1RM trend analysis
- Tracks 12 lifts: big 3, overhead, push press, pull ups, chin ups,
  incline DB, hang clean, lat pulldown
- Confirmed exact exercise names from database before building
- Plateau threshold: <3% improvement over last 4 sessions = flagged
- Results: Squat +11%, Bench +14.2%, OHP +11.7%, Lat Pulldown +6.7% — all green
- Flagged: Chin Up Weighted -15.2%, Incline DB +2%, Hang Clean -17.5%
- Hang Clean drop explained by wrist strain 2 weeks ago — important context
  that data alone can't capture (false positive case study)
- Wired plateau_detector into dashboard — visual green/red card grid
- Dashboard now shows: PR cards, plateau monitor, progression charts, AI chat
- Confirmed: VS Code play button won't launch Streamlit — terminal only for now

## Next session goals
- Deploy Atlas to Streamlit Community Cloud — get a public shareable URL
- Add exercise selector dropdown to charts (pick any lift to visualize)
- Wire plateau detection into coach.py context so Atlas can reference it
- Consider weekly check-in feature — Atlas proactively summarizes the week