import uuid

from sqlalchemy.orm import Session

from app.db.models import AuditEvent, Decision
from app.schemas.decision import DecisionCreate
from app.services.event_recorder import EventRecorder
from app.core.hashing import hash_event


def create_decision(
    db: Session,
    data: DecisionCreate,
) -> Decision:
    """
    Create a decision and its initial audit event.
    """

    decision = Decision(
        agent_id=data.agent_id,
        agent_version=data.agent_version,
        status="created",
        input_data=data.input_data,
    )

    db.add(decision)
    db.flush()

    recorder = EventRecorder(db)

    recorder.record(
        decision,
        event_type="DECISION_CREATED",
        payload={
            "agent_id": data.agent_id,
            "agent_version": data.agent_version,
        },
    )

    db.commit()
    db.refresh(decision)

    return decision


def get_decision(
    db: Session,
    decision_id: uuid.UUID,
) -> Decision | None:
    """Retrieve a decision by ID."""

    return db.get(Decision, decision_id)


def verify_decision_integrity(
    db: Session,
    decision_id: uuid.UUID,
) -> dict:
    """
    Verify the cryptographic integrity of a decision's audit chain.

    Checks:
    1. Every event's stored hash matches its contents.
    2. Every event points to the previous event's hash.
    3. The decision root hash matches the latest event.
    """

    decision = db.get(
        Decision,
        decision_id,
    )

    if decision is None:
        return {
            "valid": False,
            "reason": "Decision not found",
        }

    events = (
        db.query(AuditEvent)
        .filter(
            AuditEvent.decision_id == decision_id
        )
        .order_by(
            AuditEvent.sequence_number.asc()
        )
        .all()
    )

    if not events:
        return {
            "valid": False,
            "reason": "Decision has no audit events",
        }

    previous_hash = None

    for event in events:
        calculated_hash = hash_event(
            event_type=event.event_type,
            timestamp=event.timestamp.isoformat(),
            payload=event.payload,
            previous_hash=event.previous_hash,
        )

        if calculated_hash != event.event_hash:
            return {
                "valid": False,
                "reason": "Event hash mismatch",
                "event_id": str(event.id),
                "sequence_number": event.sequence_number,
            }

        if event.previous_hash != previous_hash:
            return {
                "valid": False,
                "reason": "Hash chain broken",
                "event_id": str(event.id),
                "sequence_number": event.sequence_number,
            }

        previous_hash = event.event_hash

    if decision.root_hash != previous_hash:
        return {
            "valid": False,
            "reason": "Decision root hash mismatch",
        }

    return {
        "valid": True,
        "event_count": len(events),
        "root_hash": decision.root_hash,
    }