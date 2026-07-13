"""
Shared state passed between nodes in the LangGraph agent graph.
"""
from typing import TypedDict, Optional, Any, Dict, List


class AgentState(TypedDict):
    user_input: str
    session_id: str
    chat_history: List[Dict[str, str]]  # [{"role": "user"/"assistant", "content": "..."}]

    tool_name: Optional[str]
    tool_args: Optional[Dict[str, Any]]
    tool_result: Optional[Dict[str, Any]]

    final_response: str
