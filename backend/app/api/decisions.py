import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.decision_service import (
    create_decision,
    get_decision,
    verify_decision_integrity,
)
from app.schemas.decision import (
    DecisionCreate,
    DecisionResponse,
    IntegrityResponse,
)


router = APIRouter(
    prefix="/api/v1/decisions",
    tags=["decisions"],
)


@router.post(
    "",
    response_model=DecisionResponse,
    status_code=201,
)
def register_decision(
    data: DecisionCreate,
    db: Session = Depends(get_db),
):
    return create_decision(db, data)

@router.get(
    "/{decision_id}/integrity",
    response_model=IntegrityResponse,
)
def check_decision_integrity(
    decision_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    result = verify_decision_integrity(
        db,
        decision_id,
    )

    if result.get("reason") == "Decision not found":
        raise HTTPException(
            status_code=404,
            detail="Decision not found",
        )

    return result

@router.get(
    "/{decision_id}",
    response_model=DecisionResponse,
)
def read_decision(
    decision_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    decision = get_decision(db, decision_id)

    if decision is None:
        raise HTTPException(
            status_code=404,
            detail="Decision not found",
        )

    return decision

