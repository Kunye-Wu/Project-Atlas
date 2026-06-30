## June 10 - Phase I: Project gets named "Atlas"

What I did:
- Built project structure
- Finished vision.md

What I learned:
- VS Code project organization
- Markdown documentation

Next step:
- Design Atlas data schema.

### June 13 — Phase II: Atlas Gets a Brain

What I did:
- Exported Hevy workout data (3934 sets, Oct 2025 → Apr 2026)
- Built load_data.py — reads and summarizes raw CSV
- Built build_database.py — creates atlas.db (SQLite)
- Built analyze.py — first real training insights

What I learned: 
- Confirmed PRs: Squat 420, Bench 335, Trap Bar Deadlift 455
- Squat peaked at 420 in Late March/Early April, slight dip since — worth investigating

- Next step:
- Fix weekly volume date parsing (strftime issue)
- Build PR detection logic — find true 1RM dates
- Start Streamlit dashboard — make Atlas visual
- Begin plateau detection algorithm

### June 14 — Phase III: Atlas Goes Visual

What I did:
- Installed Streamlit
- Built frontend/dashboard.py — first visual dashboard
- Live dashboard running at localhost:8501
- Squat progression chart working with real dates (Sep 2025 → Jun 2026)
- Bench press progression chart working
- Volume bar chart by workout type
- PR metric cards across the top (420 squat, 335 bench, 455 trap bar)
- Debugged date parsing issues — learned about pandas datetime formats

What I learned:
- Streamlit turns Python scripts into web apps instantly
- SQLite queries feed directly into charts
- Debugging is part of building — every error teaches something
- A working dashboard changes how the project feels

Next step:
- Add AI coaching layer — ask Atlas questions about your training
- Add exercise selector dropdown
- Begin Claude API integration for conversational coaching
- Plateau detection algorithm

### June 18 — Phase IV: Atlas Gets a Voice

What I did:
- Set up Claude API key and secured it in .env
- Installed anthropic + python-dotenv
- Built ai/coach.py — first AI coaching script
- Had my first real conversation with Atlas

What I learned:
- API keys need the exact ENV_VAR=value format, no shortcuts
- .env files keep secrets out of GitHub — critical habit
- Atlas isn't just printing stats — it's reasoning over real data
  and being honest about what it doesn't know
- Data quality matters as much as the AI logic — garbage in, garbage out

What stood out:
- Atlas correctly identified that recent logs were chest-heavy and
  squats were nearly absent — a real coaching insight, not a guess
- This is the first moment Project Atlas felt genuinely "alive"

Next step:
- Fix the data window so Atlas sees full lift history, not just recent sets
- Bring the chat interface into the dashboard itself

### June 20 — Phase V: Atlas Becomes Fully Interactive

What I did:
- Fixed the data window bug in coach.py — Atlas now sees full lift history
- Wired the AI coach directly into the Streamlit dashboard
- Built a real chat interface in the browser — no more terminal needed
- Asked Atlas about my bench progression and got a genuinely honest answer

What I learned:
- Streamlit blocks the terminal while running — need a second tab for other commands
- Good prompt engineering + complete data = an AI that actually reasons,
  not just agrees with you
- A chat interface inside a dashboard feels like a real product, not a script

What stood out:
- I asked Atlas about a "fast increase" in my bench and it pushed back —
  showed me the real 8-month timeline instead of just validating what I said
- That's the moment this stopped feeling like a script and started feeling
  like a coach with integrity

Next step:
- Look into deploying Atlas publicly via Streamlit Community Cloud
- Build out plateau detection as a proactive feature, not just reactive chat

### June 21 — Phase VI: Atlas Becomes Proactive

What I did:
- Built plateau_detector.py using Epley formula for estimated 1RM
- Queried the database to confirm exact exercise name spellings
- Chose which lifts to track based on actual training priorities
  (avoided bent over rows intentionally — protecting lower back)
- Wired plateau detection into the Streamlit dashboard as visual cards
- Full dashboard now live: PR cards, plateau monitor, charts, AI chat

What I learned:
- Data alone creates false positives — Hang Clean flagged as plateau
  but real reason was wrist strain + forced deload
- Athlete context is irreplaceable — the AI needs both numbers AND story
- Confirmed: exact string matching matters for database queries
  (Deadlift (Trap bar) vs Trap Bar — one character breaks everything)
- VS Code play button ≠ terminal for Streamlit — different execution contexts

What stood out:
- The dashboard now tells a complete story without being asked anything
- Green/red plateau cards make the product feel like a real coaching tool,
  not just a data viewer
- The Hang Clean false positive was actually a valuable lesson — future
  Atlas should let athletes add context notes to their training logs

Next step:
- Deploy publicly via Streamlit Community Cloud
- Add exercise selector dropdown
- Wire plateau data into the AI coach context

### June 24 — Atlas Deployment Prep

What I did:
- Generated and cleaned requirements.txt down to 5 essential packages
- Fixed ModuleNotFoundError for backend.plateau_detector in dashboard.py
- Confirmed API key setup works for Streamlit Cloud without code changes

Next step:
- Deploy Atlas publicly via share.streamlit.io — first thing tomorrow

### June 24 — Phase VII: Atlas Goes Public

What I did:
- Fixed requirements.txt for cloud deployment compatibility
- Deployed Atlas to Streamlit Community Cloud
- Added API key securely via Streamlit secrets manager
- Atlas is now live at a public URL

What I learned:
- pip freeze includes local file paths that break cloud deployment
- Use >= instead of == in requirements.txt for cloud compatibility
- Streamlit Cloud secrets manager replaces local .env files
- First deploy almost always needs a troubleshoot — persistence pays off

What stood out:
- Seeing the exact same dashboard live on the internet that was
  running locally on my Mac is a completely different feeling
- Anyone can now open a URL and talk to Atlas

Next step:
- Start fresh chat channel tomorrow
- Wire plateau detection into coach context
- Add exercise selector and athlete notes feature### June 24 — Phase VII: Atlas Goes Public

What I did:
- Fixed requirements.txt for cloud deployment compatibility
- Deployed Atlas to Streamlit Community Cloud
- Added API key securely via Streamlit secrets manager
- Atlas is now live at a public URL

What I learned:
- pip freeze includes local file paths that break cloud deployment
- Use >= instead of == in requirements.txt for cloud compatibility
- Streamlit Cloud secrets manager replaces local .env files
- First deploy almost always needs a troubleshoot — persistence pays off

What stood out:
- Seeing the exact same dashboard live on the internet that was
  running locally on my Mac is a completely different feeling
- Anyone can now open a URL and talk to Atlas

Next step:
- Start fresh chat channel tomorrow
- Wire plateau detection into coach context
- Add exercise selector and athlete notes feature

### June 25 — Phase VIII: Atlas Gets Smarter

What I did:
- Wired plateau detection into Atlas's AI context
- Built exercise selector dropdown (any lift, full history)
- Built Athlete Notes (SQLite, persistent, dashboard-integrated)

What I learned:
- Always cd to project root before running git or streamlit commands
- sys.path.insert with __file__ is the reliable way to handle imports across subdirectories
- Direct GitHub file URLs work for fetching; repo homepage doesn't navigate

What stood out:
- 3 features in one session, all working first try after fixing the path issue
- The exercise selector showing full squat history back to Sep 28 is genuinely useful

Next step:
- Wire notes into Atlas's coaching context
- Weekly check-in feature

### June 27 — Phase IX: Atlas Gets Memory & Vision

What I did:
- Wired athlete notes into Atlas coaching context
- Built conversation memory — Atlas now remembers what was said earlier in session
- Built PR detection with Plotly — gold stars on every PR date on the chart

What I learned:
- Always restart Streamlit after changing imported modules (not just refresh)
- pip3 install needed locally even if it's in requirements.txt (that's for cloud)
- Plotly gives way more control than st.line_chart for overlays and interactivity

What stood out:
- The conversation memory test was genuinely impressive — Atlas reframed
  the hang clean plateau as a recovery artifact once wrist context was given
- Seeing gold stars land exactly on Apr 3 (420 lb squat PR) felt real

Next step:
- Weekly check-in feature

### June 28 — Phase X: Atlas Becomes Proactive

What I did:
- Built weekly check-in — Atlas now initiates the conversation, not just responds
- Added delete functionality to athlete notes
- Added export to .txt for check-in summaries

What I learned:
- Data freshness problem is real and confirmed in live output
- Atlas gave an intelligent response even with stale data — proves the
  reasoning layer works, just needs fresh input
- The check-in format (This Week / Key Lifts / Flags / Recommendation)
  is the right structure — clear and actionable

What stood out:
- "Don't let one quiet week turn into two" — Atlas coaching tone is working
- The feature works exactly as designed; the constraint is data, not logic

Next step:
- CSV re-upload feature — this is the unlock that makes Atlas genuinely useful
  week over week, not just a one-time analysis tool

  ### June 29 — Phase XI: The Date Format Bug

What I did:
- Built and shipped CSV re-upload feature for fresh Hevy data
- Found and fixed a date format bug that had been silently broken since
  the database was first built on June 13
- Rebuilt the database with proper ISO date formatting

What I learned:
- SQLite doesn't parse dates automatically — it compares date strings as
  plain text unless you explicitly store them in ISO format (YYYY-MM-DD)
- A bug like this can hide for weeks because most queries either don't
  depend on precise date comparison, or happen to work by coincidence
  with small date ranges
- The bug was only exposed because real-time testing (today's actual
  workout) created a scenario where the broken comparison produced a
  visibly wrong result — historical data alone wouldn't have caught this
- Debugging methodology that worked: isolate each layer (CSV → DB → query)
  and check intermediate state at each step rather than assuming the
  whole pipeline is fine because the final output once looked correct

What stood out:
- The moment I saw "9 Oct 2025" claimed as the most recent date when it's
  clearly almost 9 months old — that's when the real cause became obvious
- After the fix, watching the weekly check-in correctly reason through my
  note about the mile run and sleep disruption felt like validation that
  the underlying architecture is sound — the bug was in data plumbing,
  not in the reasoning layer
- This is a good story for the LinkedIn post eventually: not just "I built
  a feature" but "I found and fixed a subtle bug that had been silently
  corrupting every date-based calculation for weeks"

Next step:
- README overhaul
- Goal tracking feature
- Keep building toward August demo-ready state