from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.interaction import SentimentEnum, InteractionTypeEnum, SourceEnum


class InteractionBase(BaseModel):
    hcp_name: str  # accepted as name; resolved/created server-side
    hcp_hospital: Optional[str] = None  # used only to create a new HCP if one doesn't exist
    interaction_type: InteractionTypeEnum = InteractionTypeEnum.meeting
    interaction_date: datetime
    attendees: Optional[str] = None
    topics_discussed: Optional[str] = None
    products_discussed: Optional[str] = None
    materials_shared: Optional[str] = None
    samples_distributed: Optional[str] = None
    sentiment: SentimentEnum = SentimentEnum.neutral
    outcomes: Optional[str] = None
    follow_up_actions: Optional[str] = None


class InteractionCreate(InteractionBase):
    """Used by the structured form (POST /interaction)."""
    pass


class InteractionUpdate(BaseModel):
    """All fields optional — partial update via PUT /interaction/{id}."""
    interaction_type: Optional[InteractionTypeEnum] = None
    interaction_date: Optional[datetime] = None
    attendees: Optional[str] = None
    topics_discussed: Optional[str] = None
    products_discussed: Optional[str] = None
    materials_shared: Optional[str] = None
    samples_distributed: Optional[str] = None
    sentiment: Optional[SentimentEnum] = None
    outcomes: Optional[str] = None
    follow_up_actions: Optional[str] = None
    summary: Optional[str] = None


class InteractionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hcp_id: int
    interaction_type: InteractionTypeEnum
    interaction_date: datetime
    attendees: Optional[str] = None
    topics_discussed: Optional[str] = None
    products_discussed: Optional[str] = None
    materials_shared: Optional[str] = None
    samples_distributed: Optional[str] = None
    sentiment: SentimentEnum
    outcomes: Optional[str] = None
    follow_up_actions: Optional[str] = None
    summary: Optional[str] = None
    source: SourceEnum
    created_at: datetime
    updated_at: Optional[datetime] = None
