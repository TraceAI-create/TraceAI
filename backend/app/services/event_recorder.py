import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.core.hashing import hash_event
from app.db.models import AuditEvent, Decision, DecisionEvidence, Evidence


class EventRecorder:
    """
    Central service responsible for recording audit events into the hash chain.
    """

    def __init__(self, db: Session):
        self.db = db

    def record(
        self,
        decision: Decision,
        *,
        event_type: str,
        payload: dict,
        evidence_ids: list[uuid.UUID] | None = None,
    ) -> AuditEvent:
        """
        Append a single new event to a decision's audit chain.
        """
        last_event = (
            self.db.query(AuditEvent)
            .filter(AuditEvent.decision_id == decision.id)
            .order_by(AuditEvent.sequence_number.desc())
            .first()
        )

        sequence_number = 1 if last_event is None else last_event.sequence_number + 1
        previous_hash = None if last_event is None else last_event.event_hash
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
        decision.root_hash = event_hash

        if evidence_ids:
            for ev_id in evidence_ids:
                # verify evidence exists
                ev = self.db.get(Evidence, ev_id)
                if ev:
                    link = DecisionEvidence(
                        decision_id=decision.id,
                        evidence_id=ev.id,
                        role=event_type.lower(),
                    )
                    self.db.add(link)

        return event

    def record_batch(
        self,
        decision: Decision,
        events: list[dict],
    ) -> list[AuditEvent]:
        """
        Append multiple events in deterministic sequential order.
        Each event dict: {"event_type": str, "payload": dict, "evidence_ids": list[UUID]}
        """
        created = []
        for ev in events:
            item = self.record(
                decision,
                event_type=ev["event_type"],
                payload=ev.get("payload", {}),
                evidence_ids=ev.get("evidence_ids"),
            )
            created.append(item)
            self.db.flush()  # Ensures sequence numbers advance sequentially
        return created