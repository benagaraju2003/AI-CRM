"""
REST endpoints for the structured-form interaction path:
POST /interaction, PUT /interaction/{id}, GET /interactions
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.interaction import InteractionCreate, InteractionUpdate, InteractionRead
from app.crud import interaction as interaction_crud
from app.models.interaction import SourceEnum

router = APIRouter(tags=["interactions"])


@router.post("/interaction", response_model=InteractionRead, status_code=201)
def create_interaction(payload: InteractionCreate, db: Session = Depends(get_db)):
    """Log a new interaction via the structured form."""
    return interaction_crud.create_interaction(db, payload, source=SourceEnum.form)


@router.put("/interaction/{interaction_id}", response_model=InteractionRead)
def edit_interaction(
    interaction_id: int, payload: InteractionUpdate, db: Session = Depends(get_db)
):
    """Edit an existing interaction."""
    updated = interaction_crud.update_interaction(db, interaction_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Interaction {interaction_id} not found")
    return updated


@router.get("/interactions", response_model=list[InteractionRead])
def list_interactions(
    hcp_name: str | None = Query(default=None, description="Filter by HCP name"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List interactions, optionally filtered by HCP name."""
    return interaction_crud.list_interactions(db, hcp_name=hcp_name, skip=skip, limit=limit)
