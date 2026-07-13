# Demo Video Script (10–15 minutes)

A suggested walkthrough for the submission video. Timings are approximate — adjust pacing to fit comfortably in the 10–15 minute window.

---

## 1. Intro & Understanding of the Task (1–2 min)

> "This is my submission for the AI-First CRM HCP Module — the Log Interaction screen. The core idea is that field reps shouldn't have to choose between structured data entry and natural note-taking. I built both paths so they converge on the same database record, backed by a LangGraph agent running on Groq's gemma2-9b-it model."

- State the two requirements you're demonstrating: (1) dual logging methods, (2) 5 working LangGraph tools.

## 2. Architecture Overview (2 min)

Show the README architecture diagram or draw it live:
- React + Redux frontend → FastAPI backend → PostgreSQL
- LangGraph agent sits inside the backend, called from `POST /chat`
- Explain the **router → execute_tool → respond** graph design, and briefly justify the choice not to rely on native Groq tool-calling for `gemma2-9b-it` (reliability/debuggability).

## 3. Frontend Walkthrough (2–3 min)

- Open the app at `localhost:3000`
- Point out the sidebar (Log Interaction / History), header, and the split-pane layout: structured form on the left, AI chat on the right
- Briefly walk the form fields (HCP name, type, sentiment, outcomes, etc.)

## 4. Demo: Structured Form Path (1 min)

- Fill out and submit the form for a sample HCP (e.g., "Dr. Priya Sharma")
- Show the success toast
- Switch to History tab → point out the new row with a **"Form" source badge**

## 5. Demo: All 5 LangGraph Tools via Chat (5–6 min)

Go back to Log Interaction view, use the AI chat panel for each tool in turn. Narrate what's happening in the background as each runs.

1. **`log_interaction`**
   > Type: "Met Dr Sharma today. Discussed CardioX. Positive sentiment. Requested clinical data. Follow-up next Friday."
   - Point out the reply and the "Interaction logged" tag
   - Switch to History — show the new row with a **"AI Chat" source badge**, same table as the form entry

2. **`get_hcp_profile`**
   > Type: "What's my history with Dr Sharma?"
   - Show the agent returning her profile and interaction count

3. **`edit_interaction`**
   > Type: "Change the sentiment of my last meeting with Dr Sharma to neutral."
   - Refresh History, show the sentiment badge updated

4. **`schedule_followup`**
   > Type: "Schedule a follow-up with Dr Sharma next Friday to send the Phase III PDF."
   - Explain this creates a `FollowUp` row tied to her most recent interaction

5. **`interaction_summary`**
   > Type: "Summarize my interactions with Dr Sharma."
   - Show the LLM-generated briefing reply

## 6. Code Structure Walkthrough (2–3 min)

Open the repo and briefly show:
- `backend/app/agent/graph.py` — the StateGraph, nodes, conditional edge
- `backend/app/agent/tools/` — one tool file in detail (e.g. `log_interaction.py`), pointing out the extraction prompt and the shared CRUD call
- `backend/app/crud/interaction.py` — `get_or_create_hcp` as the mechanism that makes both paths converge
- `frontend/src/redux/` — the three slices and how the chat panel dispatches `fetchInteractions()` after a successful tool call to keep the History table in sync

## 7. Closing Summary (30–60 sec)

> "To summarize: this module lets reps log interactions either by form or natural language, with a LangGraph agent that intelligently routes intent across 5 tools, all writing to one consistent PostgreSQL schema. Thanks for watching."

---

### Recording Checklist
- [ ] Backend running with a real `GROQ_API_KEY` (not the sandbox dummy key)
- [ ] PostgreSQL running and reachable
- [ ] Frontend running at `localhost:3000`
- [ ] Screen recording software capturing both browser and (briefly) the code editor
- [ ] Audio levels checked
