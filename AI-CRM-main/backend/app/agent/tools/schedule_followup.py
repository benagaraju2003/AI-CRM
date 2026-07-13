"""
Tool: schedule_followup

Creates a follow-up task tied to a specific interaction (or the HCP's most
recent one if no interaction_id is given). Resolves natural-language dates
like "next Friday" using the LLM.
"""
import json
from datetime import datetime
from typing import Optional

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from app.database import SessionLocal
from app.crud.interaction import list_interactions, create_followup
from app.agent.llm import get_llm

DATE_RESOLUTION_PROMPT = """Today's date is {today}. Convert the following natural-language
date phrase into strict ISO format YYYY-MM-DD. Return ONLY the date string, nothing else.

Phrase: "{phrase}\""""


class ScheduleFollowupArgs(BaseModel):
    hcp_name: str = Field(..., description="The doctor's name the follow-up is for.")
    due_date_phrase: str = Field(
        ..., description="Natural language date, e.g. 'next Friday', 'in 2 weeks', '2026-08-01'."
    )
    task: str = Field(..., description="What the follow-up task is, e.g. 'Send Phase III PDF'.")
    interaction_id: Optional[int] = Field(
        None, description="Specific interaction to attach this to, if known."
    )


@tool("schedule_followup", args_schema=ScheduleFollowupArgs)
def schedule_followup_tool(
    hcp_name: str, due_date_phrase: str, task: str, interaction_id: Optional[int] = None
) -> dict:
    """Schedules a follow-up task tied to an HCP interaction — e.g. 'Schedule
    a follow-up with Dr Sharma next Friday to send the Phase III PDF'. Use
    this when the user wants to create or set a reminder/next-step, as
    opposed to logging or editing an interaction's core details."""
    db = SessionLocal()
    try:
        target_interaction_id = interaction_id
        if not target_interaction_id:
            recent = list_interactions(db, hcp_name=hcp_name, limit=1)
            if not recent:
                return {
                    "success": False,
                    "error": f"No existing interaction found for '{hcp_name}' to attach a follow-up to.",
                }
            target_interaction_id = recent[0].id

        llm = get_llm(temperature=0)
        today = datetime.utcnow().strftime("%Y-%m-%d")
        resolved = llm.invoke(
            DATE_RESOLUTION_PROMPT.format(today=today, phrase=due_date_phrase)
        ).content.strip()

        try:
            due_date = datetime.strptime(resolved, "%Y-%m-%d")
        except ValueError:
            return {
                "success": False,
                "error": f"Could not resolve due date phrase '{due_date_phrase}'.",
            }

        followup = create_followup(db, target_interaction_id, due_date, task)

        return {
            "success": True,
            "followup_id": followup.id,
            "interaction_id": target_interaction_id,
            "due_date": due_date.strftime("%Y-%m-%d"),
            "task": task,
        }
    finally:
        db.close()
