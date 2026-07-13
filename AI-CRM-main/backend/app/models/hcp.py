"""
HCP (Healthcare Professional) model — represents a doctor/hospital contact.
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class HCP(Base):
    __tablename__ = "hcps"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    hospital = Column(String(255), nullable=True)
    specialty = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    interactions = relationship(
        "Interaction", back_populates="hcp", cascade="all, delete-orphan"
    )
