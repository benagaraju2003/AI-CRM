"""
CRUD operations for the HCP model. Includes get_or_create, used heavily by
both the structured form and the LangGraph log_interaction tool so that
repeated mentions of the same doctor resolve to a single HCP record.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.hcp import HCP
from app.schemas.hcp import HCPCreate


def get_hcp(db: Session, hcp_id: int) -> HCP | None:
    return db.query(HCP).filter(HCP.id == hcp_id).first()


def get_hcp_by_name(db: Session, name: str) -> HCP | None:
    return db.query(HCP).filter(func.lower(HCP.name) == func.lower(name.strip())).first()


def list_hcps(db: Session, skip: int = 0, limit: int = 100) -> list[HCP]:
    return db.query(HCP).offset(skip).limit(limit).all()


def create_hcp(db: Session, hcp: HCPCreate) -> HCP:
    db_hcp = HCP(**hcp.model_dump())
    db.add(db_hcp)
    db.commit()
    db.refresh(db_hcp)
    return db_hcp


def get_or_create_hcp(db: Session, name: str, hospital: str | None = None) -> HCP:
    """Resolve a doctor name to an HCP record, creating one if it doesn't exist.
    Used by both the form (explicit HCP selection) and the chat agent
    (extracted doctor name) to guarantee both paths hit the same table.
    """
    existing = get_hcp_by_name(db, name)
    if existing:
        return existing
    return create_hcp(db, HCPCreate(name=name.strip(), hospital=hospital))
