import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Decision
from app.schemas.decision import (
    DecisionCreate,
    DecisionResponse,
    DecisionSummaryResponse,
    IntegrityResponse,
)
from app.schemas.event import BatchEventCreate, EventCreate, EventDetailResponse
from app.schemas.review import ReviewCreate, ReviewResponse
from app.services.decision_service import (
    create_decision,
    get_decision,
    link_evidence,
    list_decisions,
    verify_decision_integrity,
)
from app.services.event_recorder import EventRecorder
from app.services.review_service import create_review, list_reviews_for_decision

router = APIRouter(
    prefix="/api/v1/decisions",
    tags=["decisions"],
)


@router.post(
    "",
    response_model=DecisionResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_decision(
    data: DecisionCreate,
    db: Session = Depends(get_db),
):
    return create_decision(db, data)


@router.get(
    "",
    response_model=list[DecisionSummaryResponse],
)
def get_decisions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    agent_id: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    return list_decisions(db, skip=skip, limit=limit, agent_id=agent_id, status=status)


@router.get(
    "/{decision_id}/integrity",
    response_model=IntegrityResponse,
)
def check_decision_integrity(
    decision_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    result = verify_decision_integrity(db, decision_id)

    if result.get("reason") == "Decision not found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    return decision


@router.post(
    "/{decision_id}/events",
    response_model=EventDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def append_event(
    decision_id: uuid.UUID,
    data: EventCreate,
    db: Session = Depends(get_db),
):
    decision = db.get(Decision, decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    recorder = EventRecorder(db)
    event = recorder.record(
        decision,
        event_type=data.event_type,
        payload=data.payload,
        evidence_ids=data.evidence_ids,
    )
    db.commit()
    db.refresh(event)
    return event


@router.post(
    "/{decision_id}/events/batch",
    response_model=list[EventDetailResponse],
    status_code=status.HTTP_201_CREATED,
)
def append_events_batch(
    decision_id: uuid.UUID,
    data: BatchEventCreate,
    db: Session = Depends(get_db),
):
    decision = db.get(Decision, decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    recorder = EventRecorder(db)
    events_dicts = [e.model_dump() for e in data.events]
    created = recorder.record_batch(decision, events_dicts)
    db.commit()
    for ev in created:
        db.refresh(ev)
    return created


@router.post(
    "/{decision_id}/evidence/{evidence_id}",
    status_code=status.HTTP_201_CREATED,
)
def attach_evidence_to_decision(
    decision_id: uuid.UUID,
    evidence_id: uuid.UUID,
    role: str = Query("context"),
    db: Session = Depends(get_db),
):
    link = link_evidence(db, decision_id, evidence_id, role=role)
    if not link:
        raise HTTPException(status_code=404, detail="Decision or Evidence not found")
    return {"message": "Evidence linked", "decision_id": str(decision_id), "evidence_id": str(evidence_id)}


@router.post(
    "/{decision_id}/reviews",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_review(
    decision_id: uuid.UUID,
    data: ReviewCreate,
    db: Session = Depends(get_db),
):
    review = create_review(db, decision_id, data)
    if not review:
        raise HTTPException(status_code=404, detail="Decision not found")
    return review


@router.get(
    "/{decision_id}/reviews",
    response_model=list[ReviewResponse],
)
def get_decision_reviews(
    decision_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    return list_reviews_for_decision(db, decision_id)
