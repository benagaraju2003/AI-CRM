"""
Interaction model — a single logged HCP interaction, created via either
the structured form or the conversational AI chat. Both paths converge here.
"""
import enum

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class SentimentEnum(str, enum.Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"


class InteractionTypeEnum(str, enum.Enum):
    meeting = "meeting"
    call = "call"
    email = "email"
    conference = "conference"
    other = "other"


class SourceEnum(str, enum.Enum):
    form = "form"
    chat = "chat"


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    hcp_id = Column(Integer, ForeignKey("hcps.id"), nullable=False)

    interaction_type = Column(Enum(InteractionTypeEnum), default=InteractionTypeEnum.meeting)
    interaction_date = Column(DateTime(timezone=True), nullable=False)

    attendees = Column(String(500), nullable=True)
    topics_discussed = Column(Text, nullable=True)
    products_discussed = Column(String(500), nullable=True)
    materials_shared = Column(String(500), nullable=True)
    samples_distributed = Column(String(500), nullable=True)

    sentiment = Column(Enum(SentimentEnum), default=SentimentEnum.neutral)
    outcomes = Column(Text, nullable=True)
    follow_up_actions = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)  # AI-generated summary

    source = Column(Enum(SourceEnum), default=SourceEnum.form)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    hcp = relationship("HCP", back_populates="interactions")
    followups = relationship(
        "FollowUp", back_populates="interaction", cascade="all, delete-orphan"
    )
