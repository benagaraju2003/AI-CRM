"""
CRUD operations for Interaction and FollowUp models.
"""
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.interaction import Interaction, SourceEnum
from app.models.followup import FollowUp
from app.schemas.interaction import InteractionCreate, InteractionUpdate
from app.crud.hcp import get_or_create_hcp


def create_interaction(
    db: Session,
    payload: InteractionCreate,
    source: SourceEnum = SourceEnum.form,
    summary: str | None = None,
) -> Interaction:
    hcp = get_or_create_hcp(db, payload.hcp_name, hospital=payload.hcp_hospital)

    db_interaction = Interaction(
        hcp_id=hcp.id,
        interaction_type=payload.interaction_type,
        interaction_date=payload.interaction_date,
        attendees=payload.attendees,
        topics_discussed=payload.topics_discussed,
        products_discussed=payload.products_discussed,
        materials_shared=payload.materials_shared,
        samples_distributed=payload.samples_distributed,
        sentiment=payload.sentiment,
        outcomes=payload.outcomes,
        follow_up_actions=payload.follow_up_actions,
        summary=summary,
        source=source,
    )
    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)
    return db_interaction


def get_interaction(db: Session, interaction_id: int) -> Interaction | None:
    return db.query(Interaction).filter(Interaction.id == interaction_id).first()


def list_interactions(
    db: Session,
    hcp_name: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Interaction]:
    query = db.query(Interaction)
    if hcp_name:
        query = query.join(Interaction.hcp).filter(
            Interaction.hcp.has(name=hcp_name)
        )
    return query.order_by(Interaction.interaction_date.desc()).offset(skip).limit(limit).all()


def update_interaction(
    db: Session, interaction_id: int, payload: InteractionUpdate
) -> Interaction | None:
    db_interaction = get_interaction(db, interaction_id)
    if not db_interaction:
        return None

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_interaction, field, value)

    db.commit()
    db.refresh(db_interaction)
    return db_interaction


def create_followup(
    db: Session, interaction_id: int, due_date: datetime, task: str
) -> FollowUp:
    db_followup = FollowUp(interaction_id=interaction_id, due_date=due_date, task=task)
    db.add(db_followup)
    db.commit()
    db.refresh(db_followup)
    return db_followup
