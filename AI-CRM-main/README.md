# AI-First HCP CRM — Log Interaction Module

A CRM module for pharmaceutical field reps to log Healthcare Professional (HCP) interactions via **two converging paths**: a structured form and a conversational AI assistant. Both write to the same PostgreSQL schema, powered by a LangGraph agent running on Groq (`gemma2-9b-it`).

Built for the Naukri Round 1 Technical & Development Task.

---

## 1. Overview

Field reps generate most of their interaction data as unstructured notes ("Met Dr Sharma, discussed CardioX, follow up Friday"). This module lets them either:

- Fill out a structured form, **or**
- Type/paste a free-text note into the AI chat panel

...and have both routes land in the same `interactions` table, so downstream reporting doesn't care which path was used.

## 2. Architecture

```
┌─────────────────┐        ┌──────────────────────┐        ┌─────────────┐
│  React Frontend  │──────▶│   FastAPI Backend     │──────▶│  PostgreSQL │
│  (Redux Toolkit)  │◀──────│                        │◀──────│             │
└─────────────────┘        │  ┌──────────────────┐  │        └─────────────┘
                             │  │ LangGraph Agent   │  │
                             │  │  router → tool →  │  │──────▶ Groq API
                             │  │  respond           │  │        (gemma2-9b-it)
                             │  └──────────────────┘  │
                             └──────────────────────┘
```

**Two entry points, one schema:**
- `POST /interaction` → structured form → `Interaction(source="form")`
- `POST /chat` → LangGraph agent → `log_interaction` tool → `Interaction(source="chat")`

### LangGraph Agent Design

The agent uses a **router → execute_tool → respond** graph rather than relying on Groq's native function-calling:

```
START → router → (tool chosen?) → execute_tool → respond → END
                 └─(no tool)────────────────────────▶ respond → END
```

**Why not native tool-calling?** `gemma2-9b-it` has inconsistent support for OpenAI-style function calling compared to Llama models on Groq. Instead, the `router` node prompts the LLM to return strict JSON naming which of the 5 tools to call and with what arguments. This is more reliable, fully debuggable, and keeps tool selection under explicit control — a deliberate engineering decision.

### The 5 LangGraph Tools

| Tool | Purpose |
|---|---|
| `log_interaction` | Extracts doctor name, hospital, interaction type, products, sentiment, outcomes, and follow-up date from free text via the LLM, then saves a new interaction. |
| `edit_interaction` | Modifies an existing interaction, found by ID or by HCP name (defaults to their most recent interaction). |
| `get_hcp_profile` | Retrieves an HCP's profile plus their recent interaction history. |
| `schedule_followup` | Creates a follow-up task tied to an interaction, resolving natural-language dates ("next Friday") via the LLM. |
| `interaction_summary` | Generates an LLM briefing across one HCP's or all recent interactions. |

## 3. Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Redux Toolkit, React Router, Axios, Inter font |
| Backend | FastAPI, SQLAlchemy, Pydantic |
| AI | LangGraph, LangChain, Groq (`gemma2-9b-it`) |
| Database | PostgreSQL |

## 4. Folder Structure

```
hcp-crm-ai/
├── backend/
│   └── app/
│       ├── main.py              # FastAPI entrypoint
│       ├── config.py            # env-based settings
│       ├── database.py          # SQLAlchemy engine/session
│       ├── models/               # HCP, Interaction, FollowUp
│       ├── schemas/              # Pydantic request/response models
│       ├── crud/                 # DB operations (shared by both logging paths)
│       ├── routes/               # /interaction(s), /chat
│       ├── agent/
│       │   ├── graph.py          # LangGraph StateGraph
│       │   ├── state.py          # AgentState
│       │   ├── llm.py            # Groq client
│       │   └── tools/            # the 5 tools
│       └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/           # layout, form, chat, history
│       ├── pages/Dashboard.jsx
│       ├── redux/                # interactions, chat, ui slices
│       └── services/api.js
├── README.md
└── demo_script.md
```

## 5. Environment Variables

**`backend/.env`** (copy from `.env.example`):
```
DATABASE_URL=postgresql://postgres:password@localhost:5432/hcp_crm
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=gemma2-9b-it
CORS_ORIGINS=http://localhost:3000
ENV=development
```

**`frontend/.env`** (copy from `.env.example`):
```
REACT_APP_API_BASE_URL=http://localhost:8000
```

Get a Groq API key at [console.groq.com](https://console.groq.com/keys). Never commit `.env` files — only `.env.example` is checked in.

## 6. Database Setup

```bash
# Using local PostgreSQL
createdb hcp_crm
# Or with Docker:
docker run --name hcp-postgres -e POSTGRES_PASSWORD=password -e POSTGRES_DB=hcp_crm -p 5432:5432 -d postgres:16
```

Tables are created automatically on backend startup via `Base.metadata.create_all()` — no separate migration step needed for this deliverable.

## 7. Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then fill in DATABASE_URL and GROQ_API_KEY
uvicorn app.main:app --reload --port 8000
```

Backend runs at `http://localhost:8000`. Interactive API docs: `http://localhost:8000/docs`.

## 8. Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
npm start
```

Frontend runs at `http://localhost:3000`.

## 9. Running the Full Project

1. Start PostgreSQL
2. Start the backend (`uvicorn app.main:app --reload --port 8000`)
3. Start the frontend (`npm start`)
4. Open `http://localhost:3000`

## 10. API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/interaction` | Log a new interaction via the structured form |
| `PUT` | `/interaction/{id}` | Edit an existing interaction |
| `GET` | `/interactions?hcp_name=` | List interactions, optionally filtered by HCP |
| `POST` | `/chat` | Send a message to the LangGraph agent |
| `GET` | `/health` | Health check |

## 11. Known Limitations / Future Work

- Chat session history is in-memory (resets on backend restart) — fine for a demo, would move to Redis/DB for multi-instance production use.
- No auth layer — out of scope for this assignment.
- Table creation via `create_all()` rather than Alembic migrations, for a single-environment deliverable.
- Voice-note-to-text (shown in the original mockup) is not implemented; the AI chat text input covers the same "unstructured input → structured data" requirement.

## 12. Screenshots

_[Insert screenshots here before submission: split-pane Log Interaction view, AI chat mid-conversation, Interaction History table]_

---

See `demo_script.md` for the 10–15 minute video walkthrough script.
