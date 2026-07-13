"""
Tool: interaction_summary

Generates an LLM summary across an HCP's recent interactions (or all
recent interactions if no HCP is specified) — e.g. "Summarize my week
with Dr Sharma" or "Summarize all my interactions this week".
"""
from typing import Optional

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from app.database import SessionLocal
from app.crud.interaction import list_interactions
from app.agent.llm import get_llm

SUMMARY_PROMPT = """You are assisting a pharmaceutical field rep. Summarize the following
logged HCP interactions into a concise, professional briefing (3-5 sentences). Highlight
key themes, sentiment trends, and any open follow-ups.

Interactions:
{interactions_text}

Write the summary now."""


class InteractionSummaryArgs(BaseModel):
    hcp_name: Optional[str] = Field(
        None, description="Limit the summary to this HCP. Omit to summarize recent activity across all HCPs."
    )
    limit: int = Field(10, description="Max number of interactions to include.")


@tool("interaction_summary", args_schema=InteractionSummaryArgs)
def interaction_summary_tool(hcp_name: Optional[str] = None, limit: int = 10) -> dict:
    """Generates a natural-language summary across multiple logged
    interactions — e.g. 'Summarize my interactions with Dr Sharma' or
    'Give me a summary of this week'. Use this when the user wants an
    overview or briefing rather than a single interaction's details."""
    db = SessionLocal()
    try:
        interactions = list_interactions(db, hcp_name=hcp_name, limit=limit)
        if not interactions:
            scope = f"for '{hcp_name}'" if hcp_name else "logged"
            return {"success": False, "error": f"No interactions {scope} found."}

        interactions_text = "\n".join(
            f"- [{i.interaction_date.strftime('%Y-%m-%d')}] {i.hcp.name} "
            f"({i.interaction_type.value}, sentiment: {i.sentiment.value}): "
            f"{i.summary or i.topics_discussed or 'No details recorded.'}"
            for i in interactions
        )

        llm = get_llm(temperature=0.3)
        response = llm.invoke(SUMMARY_PROMPT.format(interactions_text=interactions_text))

        return {
            "success": True,
            "hcp_name": hcp_name,
            "interactions_included": len(interactions),
            "summary": response.content.strip(),
        }
    finally:
        db.close()
