"""
REST endpoint for the conversational AI chat path: POST /chat
"""
from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse
from app.agent.graph import run_agent

router = APIRouter(tags=["chat"])

# In-memory per-session chat history (fine for a single-instance demo app;
# would move to Redis/DB for production multi-instance deployment).
_SESSION_HISTORY: dict[str, list[dict]] = {}


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    """Send a free-text message to the LangGraph agent. The agent decides
    whether to log an interaction, edit one, look up an HCP profile,
    schedule a follow-up, or summarize — and returns a natural-language reply."""
    session_id = payload.session_id or "default"
    history = _SESSION_HISTORY.setdefault(session_id, [])

    result = run_agent(payload.message, session_id=session_id, chat_history=history)

    history.append({"role": "user", "content": payload.message})
    history.append({"role": "assistant", "content": result["reply"]})

    return ChatResponse(
        reply=result["reply"],
        tool_used=result["tool_used"],
        data=result["data"],
        history=history,
    )
