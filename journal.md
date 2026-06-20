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