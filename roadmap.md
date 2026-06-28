# Project Atlas — Roadmap
Last updated: June 27, 2026

## Phase 0 — Design (June 1–7) ✅ COMPLETE
Goal: Design before coding.
- Researched Hevy, Strong, RP Hypertrophy, MacroFactor, Whoop, Juggernaut AI
- Defined inputs: training (exercise, sets, reps, weight)
- Created project requirements, vision.md, folder structure
- Chose stack: Streamlit, Python, SQLite, Claude API

## Phase 1 — Foundation (June 8–30) ✅ COMPLETE (ahead of schedule)
Goal: Working MVP.
- Exported Hevy data (3,934 sets, Oct 2025 → June 2026)
- Built SQLite database (atlas.db)
- Built Streamlit dashboard with PR cards, progression charts, volume breakdown
- Deployed publicly: https://project-atlas-8vwappjmulurmuarlbfbgcc.streamlit.app

## Phase 2 — Intelligence (July 1–31) ✅ LARGELY COMPLETE (ahead of schedule)
Goal: AI Coach V1
- Claude API integrated — Atlas answers questions about training
- Plateau detection (Epley e1RM trend, 12 lifts tracked)
- Athlete notes — personal context Atlas can reference
- Conversation memory — real back-and-forth coaching sessions
- PR detection — gold star markers on progression charts
- Plateau status wired into AI context

### Remaining Phase 2 goals
- Weekly check-in — Atlas proactively summarizes the week
- Next training block recommendation
- Delete/edit athlete notes

## Phase 3 — Make It Impressive (August 1–28)
Goal: Production-quality coaching platform.

### Data freshness (NEW — critical infrastructure)
- CSV re-upload button in dashboard — user imports new Hevy export,
  Atlas rebuilds database automatically
- Explore Hevy API for automatic data sync (no manual export needed)
- Long-term: in-app workout logging so Atlas becomes source of truth,
  not dependent on Hevy exports

### Coaching features
- PR prediction — forecast when next PR attempt is viable
- Training block generation — Atlas designs next 4-week program
- Weekly reports — automated Sunday summary email or dashboard card
- Performance forecasting — trajectory modeling for key lifts

### Product quality
- Natural language interface improvements
- Response quality tuning — more specific, less generic
- Mobile-friendly dashboard layout

### Stretch goal — Multi-agent architecture
- Agent 1: Training analyst
- Agent 2: Nutrition analyst
- Agent 3: Recovery analyst
- Agent 4: Head coach (combines all three)

## Resume Outcome (target: August 28)
Built an AI-powered fitness coaching platform that analyzes workout data
to generate personalized training recommendations, fatigue assessments,
PR forecasts, and adaptive programming using LLM agents and predictive
analytics. Deployed publicly with real multi-year training data.