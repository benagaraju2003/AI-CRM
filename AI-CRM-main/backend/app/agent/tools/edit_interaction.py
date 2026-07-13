"""
Tool: edit_interaction

Modifies an existing logged interaction. Supports lookup either by explicit
interaction_id, or by hcp_name (resolves to that HCP's most recent
interaction) so users can say things like "Change the sentiment of my
meeting with Dr Sharma to positive" without knowing the record ID.
"""
from typing import Optional

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from app.database import SessionLocal
from app.crud.interaction import get_interaction, update_interaction, list_interactions
from app.schemas.interaction import InteractionUpdate
from app.models.interaction import SentimentEnum, InteractionTypeEnum


class EditInteractionArgs(BaseModel):
    interaction_id: Optional[int] = Field(
        None, description="The ID of the interaction to edit, if known."
    )
    hcp_name: Optional[str] = Field(
        None,
        description="Doctor's name — used to find their most recent interaction if interaction_id is not known.",
    )
    outcomes: Optional[str] = Field(None, description="Updated outcomes text.")
    sentiment: Optional[str] = Field(
        None, description="Updated sentiment: 'positive', 'neutral', or 'negative'."
    )
    follow_up_actions: Optional[str] = Field(None, description="Updated follow-up actions text.")
    topics_discussed: Optional[str] = Field(None, description="Updated topics discussed.")
    products_discussed: Optional[str] = Field(None, description="Updated products discussed.")


@tool("edit_interaction", args_schema=EditInteractionArgs)
def edit_interaction_tool(
    interaction_id: Optional[int] = None,
    hcp_name: Optional[str] = None,
    outcomes: Optional[str] = None,
    sentiment: Optional[str] = None,
    follow_up_actions: Optional[str] = None,
    topics_discussed: Optional[str] = None,
    products_discussed: Optional[str] = None,
) -> dict:
    """Edits an already-logged interaction — e.g. correcting the sentiment,
    updating outcomes, or adding follow-up notes. Identify the target
    interaction either by its ID or by the HCP's name (uses their most
    recent interaction). Use this when the user wants to change or correct
    a previously logged interaction rather than log a new one."""
    db = SessionLocal()
    try:
        target_id = interaction_id

        if not target_id and hcp_name:
            recent = list_interactions(db, hcp_name=hcp_name, limit=1)
            if not recent:
                return {"success": False, "error": f"No interactions found for '{hcp_name}'."}
            target_id = recent[0].id

        if not target_id:
            return {
                "success": False,
                "error": "Provide either an interaction_id or an hcp_name to identify the record to edit.",
            }

        existing = get_interaction(db, target_id)
        if not existing:
            return {"success": False, "error": f"Interaction {target_id} not found."}

        update_payload = InteractionUpdate(
            outcomes=outcomes,
            sentiment=SentimentEnum(sentiment) if sentiment else None,
            follow_up_actions=follow_up_actions,
            topics_discussed=topics_discussed,
            products_discussed=products_discussed,
        )
        updated = update_interaction(db, target_id, update_payload)

        return {
            "success": True,
            "interaction_id": updated.id,
            "updated_fields": update_payload.model_dump(exclude_unset=True, exclude_none=True),
        }
    finally:
        db.close()
