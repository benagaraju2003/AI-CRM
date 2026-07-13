"""
Tool: get_hcp_profile

Retrieves an HCP's profile and recent interaction history — used both to
answer direct questions ("What's my history with Dr Sharma?") and as
context the agent can use before logging or summarizing.
"""
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from app.database import SessionLocal
from app.crud.hcp import get_hcp_by_name
from app.crud.interaction import list_interactions


class GetHCPProfileArgs(BaseModel):
    hcp_name: str = Field(..., description="The doctor's name to look up.")


@tool("get_hcp_profile", args_schema=GetHCPProfileArgs)
def get_hcp_profile_tool(hcp_name: str) -> dict:
    """Retrieves an HCP's profile (hospital, specialty, contact info) along
    with a summary of their recent logged interactions. Use this when the
    user asks about a doctor's history, past visits, or profile details."""
    db = SessionLocal()
    try:
        hcp = get_hcp_by_name(db, hcp_name)
        if not hcp:
            return {"success": False, "error": f"No HCP found matching '{hcp_name}'."}

        interactions = list_interactions(db, hcp_name=hcp.name, limit=10)

        return {
            "success": True,
            "hcp": {
                "id": hcp.id,
                "name": hcp.name,
                "hospital": hcp.hospital,
                "specialty": hcp.specialty,
            },
            "total_interactions": len(interactions),
            "recent_interactions": [
                {
                    "id": i.id,
                    "date": i.interaction_date.isoformat(),
                    "type": i.interaction_type.value,
                    "sentiment": i.sentiment.value,
                    "products_discussed": i.products_discussed,
                    "summary": i.summary or i.topics_discussed,
                }
                for i in interactions
            ],
        }
    finally:
        db.close()
