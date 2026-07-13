"""
LangGraph agent graph for the HCP CRM chat interface.

Flow:
    START -> router -> [execute_tool -> respond | respond] -> END

- router: prompts the LLM to decide which of the 5 tools (if any) fits the
  user's message, and to extract the arguments for it, as strict JSON.
- execute_tool: dispatches to the actual Python tool function and runs it
  against the database.
- respond: turns the tool result (or, for general chat, the router's own
  reply) into a natural-language message for the user.
"""
import json

from langgraph.graph import StateGraph, START, END

from app.agent.state import AgentState
from app.agent.llm import get_llm
from app.agent.tools.log_interaction import log_interaction_tool
from app.agent.tools.edit_interaction import edit_interaction_tool
from app.agent.tools.get_hcp_profile import get_hcp_profile_tool
from app.agent.tools.schedule_followup import schedule_followup_tool
from app.agent.tools.interaction_summary import interaction_summary_tool

TOOLS = {
    "log_interaction": log_interaction_tool,
    "edit_interaction": edit_interaction_tool,
    "get_hcp_profile": get_hcp_profile_tool,
    "schedule_followup": schedule_followup_tool,
    "interaction_summary": interaction_summary_tool,
}

ROUTER_PROMPT = """You are the routing brain of an AI-first pharmaceutical CRM assistant.
Given the user's message and recent conversation, decide which ONE tool (if any) should
handle it, and extract the arguments needed to call it.

Available tools:
1. log_interaction(raw_text) — user is describing a new HCP interaction to log.
2. edit_interaction(interaction_id?, hcp_name?, outcomes?, sentiment?, follow_up_actions?,
   topics_discussed?, products_discussed?) — user wants to correct/update an existing logged interaction.
3. get_hcp_profile(hcp_name) — user is asking about a doctor's profile or history.
4. schedule_followup(hcp_name, due_date_phrase, task, interaction_id?) — user wants to
   set/create a follow-up reminder or next step.
5. interaction_summary(hcp_name?, limit?) — user wants a summary/briefing across interactions.

Conversation so far:
{history}

User's latest message:
\"\"\"{message}\"\"\"

Return STRICT JSON only, no markdown, no commentary, in this exact shape:
{{"tool": "<one of: log_interaction, edit_interaction, get_hcp_profile, schedule_followup, interaction_summary, none>", "args": {{...}}}}

If the message is general conversation, a greeting, or doesn't match any tool, use "tool": "none"
and an empty args object.

For log_interaction specifically, pass the user's ENTIRE message as raw_text so no detail is lost.

JSON only:"""

RESPONSE_PROMPT = """You are a helpful AI assistant embedded in a pharmaceutical CRM, speaking
to a field rep. Given the tool that was run and its result, write a short, natural,
professional reply (2-4 sentences) confirming what happened. If the tool failed, explain
briefly and suggest what info is missing. Do not mention "JSON" or internal mechanics.

Tool called: {tool_name}
Tool result: {tool_result}

User's original message: "{message}"

Reply:"""

NO_TOOL_RESPONSE_PROMPT = """You are a helpful AI assistant embedded in a pharmaceutical CRM.
The user's message didn't match a specific CRM action. Reply conversationally and briefly
(1-3 sentences), and if relevant, remind them they can log interactions, ask about an HCP's
history, schedule follow-ups, edit past entries, or request a summary.

User's message: "{message}"

Reply:"""


def _parse_router_json(content: str) -> dict:
    cleaned = content.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(cleaned)


def router_node(state: AgentState) -> AgentState:
    """Decides which tool (if any) to invoke based on user intent."""
    llm = get_llm(temperature=0)
    history_text = "\n".join(
        f"{turn['role']}: {turn['content']}" for turn in state.get("chat_history", [])[-6:]
    ) or "(no prior messages)"

    prompt = ROUTER_PROMPT.format(history=history_text, message=state["user_input"])
    response = llm.invoke(prompt)

    try:
        parsed = _parse_router_json(response.content)
        tool_name = parsed.get("tool")
        tool_args = parsed.get("args", {})
    except (json.JSONDecodeError, AttributeError):
        tool_name, tool_args = "none", {}

    if tool_name not in TOOLS:
        tool_name, tool_args = None, {}

    return {**state, "tool_name": tool_name, "tool_args": tool_args}


def route_decision(state: AgentState) -> str:
    """Conditional edge: go to execute_tool if a valid tool was chosen, else respond directly."""
    return "execute_tool" if state.get("tool_name") else "respond"


def execute_tool_node(state: AgentState) -> AgentState:
    """Runs the chosen tool with the extracted arguments."""
    tool_name = state["tool_name"]
    tool_args = state.get("tool_args") or {}
    tool_fn = TOOLS[tool_name]

    try:
        result = tool_fn.invoke(tool_args)
    except Exception as exc:  # noqa: BLE001 — surface any tool failure to the user gracefully
        result = {"success": False, "error": f"Tool execution failed: {exc}"}

    return {**state, "tool_result": result}


def respond_node(state: AgentState) -> AgentState:
    """Generates the final natural-language reply."""
    llm = get_llm(temperature=0.3)

    if state.get("tool_name") and state.get("tool_result") is not None:
        prompt = RESPONSE_PROMPT.format(
            tool_name=state["tool_name"],
            tool_result=json.dumps(state["tool_result"]),
            message=state["user_input"],
        )
    else:
        prompt = NO_TOOL_RESPONSE_PROMPT.format(message=state["user_input"])

    response = llm.invoke(prompt)
    return {**state, "final_response": response.content.strip()}


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("router", router_node)
    graph.add_node("execute_tool", execute_tool_node)
    graph.add_node("respond", respond_node)

    graph.add_edge(START, "router")
    graph.add_conditional_edges(
        "router", route_decision, {"execute_tool": "execute_tool", "respond": "respond"}
    )
    graph.add_edge("execute_tool", "respond")
    graph.add_edge("respond", END)

    return graph.compile()


# Compiled once at import time and reused across requests.
agent_graph = build_graph()


def run_agent(message: str, session_id: str = "default", chat_history: list[dict] | None = None) -> dict:
    """Entry point called by the /chat route."""
    initial_state: AgentState = {
        "user_input": message,
        "session_id": session_id,
        "chat_history": chat_history or [],
        "tool_name": None,
        "tool_args": None,
        "tool_result": None,
        "final_response": "",
    }
    final_state = agent_graph.invoke(initial_state)
    return {
        "reply": final_state["final_response"],
        "tool_used": final_state.get("tool_name"),
        "data": final_state.get("tool_result"),
    }
