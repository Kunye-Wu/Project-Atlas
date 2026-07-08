# Project Atlas — Roadmap
Last updated: July 7, 2026

## Phase 0 — Design (June 1–7) ✅ COMPLETE
Goal: Design before coding.
- Researched Hevy, Strong, RP Hypertrophy, MacroFactor, Whoop, Juggernaut AI
- Defined inputs: training (exercise, sets, reps, weight)
- Created project requirements, vision.md, folder structure
- Chose stack: Streamlit, Python, SQLite, Claude API

## Phase 1 — Foundation (June 8–30) ✅ COMPLETE (ahead of schedule)
Goal: Working MVP.
- Exported Hevy data (4,100+ sets, Sep 2025 → Jul 2026)
- Built SQLite database (atlas.db) with ISO date formatting
- Built Streamlit dashboard with PR cards, progression charts, volume breakdown
- Deployed publicly: https://project-atlas-8vwappjmulurmuarlbfbgcc.streamlit.app

## Phase 2 — Intelligence (July 1–31) ✅ COMPLETE (finished July 7)
Goal: AI Coach V1
- Claude API integrated — Atlas answers questions about training
- Plateau detection (Epley e1RM trend, 12 lifts tracked)
- Athlete notes — personal context Atlas can reference
- Conversation memory — real back-and-forth coaching sessions
- PR detection — gold star markers on Plotly progression charts
- Plateau status, athlete notes, and goals wired into AI context
- Weekly check-in — Atlas proactively summarizes the week
- Goal tracking — progress bars, weekly rate, ETA forecasting
- CSV re-upload — live data sync from Hevy export, no terminal needed
- Dynamic PR metric cards — pull from database, auto-update on sync
- Delete buttons for goals and athlete notes
- Fixed critical date format bug — ISO conversion for SQLite compatibility

## Phase 3 — Make It Impressive ✅ COMPLETE (finished July 7)
Goal: Production-quality coaching platform.

### Data freshness ✅
- CSV re-upload button — user imports new Hevy export, Atlas rebuilds instantly
- ISO date format fix — all date-based queries now work correctly
- Long-term: Hevy API integration (not yet built)

### Product quality ✅
- Professional README — badges, architecture diagram, feature list, live demo link
- Demo GIF (3:35) autoplaying on GitHub repo homepage
- Dynamic PR cards pulling from live database
- Exercise selector dropdown — any lift visualizable with PR markers

### README overhaul ✅
- Architecture diagram
- Full feature list
- Demo GIF showing dashboard live
- Tech stack badges
- Live demo link + GitHub link

## Resume Outcome ✅ ACHIEVED (July 7, 2026)
Built an AI-powered fitness coaching platform that analyzes 4,100+ real
workout sets to generate personalized training recommendations, plateau
detection, proactive weekly coaching, goal forecasting, and context-aware
reasoning using the Claude API. Deployed publicly with a live demo GIF
on GitHub. LinkedIn post published July 7, 2026.

## What's Next (Future Phases)
- Hevy API integration — automatic data sync, no manual CSV export
- In-app workout logging — Atlas becomes the source of truth
- Training block generation — Atlas designs next 4-week program
- PR prediction — forecast when next PR attempt is viable
- Mobile-friendly dashboard layout
- Multi-agent architecture (Training + Nutrition + Recovery + Head Coach)
- Goal tracking: "Road to 450 squat" — % complete, estimated timeline