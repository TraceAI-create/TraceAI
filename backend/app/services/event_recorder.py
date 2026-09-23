from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.hashing import hash_event
from app.db.models import AuditEvent, Decision


class EventRecorder:
    """
    Central service responsible for recording audit events.

    Every observable action in TraceAI should eventually pass
    through this component.
    """

    def __init__(self, db: Session):
        self.db = db

    def record(
        self,
        decision: Decision,
        *,
        event_type: str,
        payload: dict,
    ) -> AuditEvent:
        """
        Append a new event to a decision's audit chain.
        """

        last_event = (
            self.db.query(AuditEvent)
            .filter(
                AuditEvent.decision_id == decision.id
            )
            .order_by(
                AuditEvent.sequence_number.desc()
            )
            .first()
        )

        if last_event is None:
            sequence_number = 1
            previous_hash = None
        else:
            sequence_number = (
                last_event.sequence_number + 1
            )
            previous_hash = last_event.event_hash

        timestamp = datetime.now(timezone.utc)

        event_hash = hash_event(
            event_type=event_type,
            timestamp=timestamp.isoformat(),
            payload=payload,
            previous_hash=previous_hash,
        )

        event = AuditEvent(
            decision_id=decision.id,
            event_type=event_type,
            sequence_number=sequence_number,
            timestamp=timestamp,
            payload=payload,
            previous_hash=previous_hash,
            event_hash=event_hash,
        )

        self.db.add(event)

        # The root hash always points to the newest event.
        decision.root_hash = event_hash

        return event