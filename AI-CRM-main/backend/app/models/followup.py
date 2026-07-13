"""
FollowUp model — a scheduled next-step tied to an interaction, created by
the schedule_followup LangGraph tool or manually via the form.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class FollowUp(Base):
    __tablename__ = "followups"

    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(Integer, ForeignKey("interactions.id"), nullable=False)

    due_date = Column(DateTime(timezone=True), nullable=False)
    task = Column(Text, nullable=False)
    completed = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    interaction = relationship("Interaction", back_populates="followups")
