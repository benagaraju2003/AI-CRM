from typing import Optional, List, Any, Dict

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"


class ChatResponse(BaseModel):
    reply: str
    tool_used: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    history: List[Dict[str, str]] = []
