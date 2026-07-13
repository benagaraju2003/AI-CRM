"""
Tool: log_interaction

Captures a new HCP interaction from free-text rep notes. Uses the LLM to
extract structured entities (doctor name, hospital, interaction type,
products, sentiment, follow-up date, summary), then writes a new
Interaction row via the same CRUD path used by the structured form —
guaranteeing both logging methods converge on identical, consistent data.
"""
import json
from datetime import datetime, timedelta

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from app.database import SessionLocal
from app.crud.interaction import create_interaction, create_followup
from app.schemas.interaction import InteractionCreate
from app.models.interaction import InteractionTypeEnum, SentimentEnum, SourceEnum
from app.agent.llm import get_llm

EXTRACTION_PROMPT = """You are a data extraction engine for a pharmaceutical sales CRM.
Extract the following fields from the field rep's note and return STRICT JSON only.
Do not include markdown code fences, explanations, or any text outside the JSON object.

Required JSON shape:
{{
  "hcp_name": string,
  "hospital": string or null,
  "interaction_type": one of ["meeting", "call", "email", "conference", "other"],
  "products_discussed": string or null (comma-separated if multiple),
  "topics_discussed": string,
  "sentiment": one of ["positive", "neutral", "negative"],
  "outcomes": string or null,
  "follow_up_date": string in YYYY-MM-DD format, or null if none mentioned,
  "summary": a concise 1-2 sentence summary of the interaction
}}

Today's date is {today}. Resolve relative dates (e.g. "next Friday", "tomorrow") against it.

Rep's note:
\"\"\"{text}\"\"\"

Return JSON only, nothing else."""


class LogInteractionArgs(BaseModel):
    raw_text: str = Field(
        ...,
        description=(
            "The field rep's free-text note describing the interaction, e.g. "
            "'Met Dr Sharma today. Discussed CardioX. Requested clinical data. "
            "Follow-up next Friday.'"
        ),
    )


def _parse_llm_json(content: str) -> dict:
    cleaned = content.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(cleaned)


def _resolve_follow_up_date(date_str: str | None) -> datetime | None:
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None


@tool("log_interaction", args_schema=LogInteractionArgs)
def log_interaction_tool(raw_text: str) -> dict:
    """Extracts structured interaction data (doctor name, hospital, products
    discussed, sentiment, outcomes, follow-up date) from a free-text rep note
    using the LLM, then saves it as a new interaction record. Use this when
    the user describes an HCP interaction they want logged, e.g. 'Met Dr
    Sharma today, discussed CardioX, follow up next Friday.'"""
    llm = get_llm(temperature=0)
    today = datetime.utcnow().strftime("%Y-%m-%d")
    prompt = EXTRACTION_PROMPT.format(text=raw_text, today=today)

    response = llm.invoke(prompt)
    try:
        extracted = _parse_llm_json(response.content)
    except json.JSONDecodeError:
        return {
            "success": False,
            "error": "Could not parse structured data from the note. Please rephrase.",
            "raw_llm_output": response.content,
        }

    hcp_name = extracted.get("hcp_name")
    if not hcp_name:
        return {"success": False, "error": "Could not identify an HCP name in the note."}

    db = SessionLocal()
    try:
        payload = InteractionCreate(
            hcp_name=hcp_name,
            hcp_hospital=extracted.get("hospital"),
            interaction_type=InteractionTypeEnum(extracted.get("interaction_type") or "meeting"),
            interaction_date=datetime.utcnow(),
            products_discussed=extracted.get("products_discussed"),
            topics_discussed=extracted.get("topics_discussed"),
            sentiment=SentimentEnum(extracted.get("sentiment") or "neutral"),
            outcomes=extracted.get("outcomes"),
            follow_up_actions=(
                f"Follow up on {extracted['follow_up_date']}"
                if extracted.get("follow_up_date")
                else None
            ),
        )
        interaction = create_interaction(
            db, payload, source=SourceEnum.chat, summary=extracted.get("summary")
        )

        follow_up_dt = _resolve_follow_up_date(extracted.get("follow_up_date"))
        if follow_up_dt:
            create_followup(db, interaction.id, follow_up_dt, f"Follow up with {hcp_name}")

        return {
            "success": True,
            "interaction_id": interaction.id,
            "hcp_name": hcp_name,
            "summary": extracted.get("summary"),
            "extracted_fields": extracted,
        }
    finally:
        db.close()
