from datetime import datetime, timezone
from typing import Any, Literal
from uuid import UUID
import httpx

from traceai_sdk.client import TraceAIClient
from traceai_sdk.exceptions import TraceAIIntegrityError
from traceai_sdk.hashing import hash_event
from traceai_sdk.models import AuditEventRecord, DecisionSession, EvidenceRef, IntegrityCheckResult


class DecisionContext:
    """
    Context manager for instrumenting an AI Agent execution.

    Usage:
        with DecisionContext(agent_id="my_agent", agent_version="1.0.0") as ctx:
            ctx.record_event("PLAN", {"steps": [...]})
            ev = ctx.record_evidence("document", {"file": "content"})
            ctx.record_event("ACTION", {"approved": True})
    """

    def __init__(
        self,
        agent_id: str,
        agent_version: str,
        input_data: dict[str, Any] | None = None,
        endpoint: str = "http://localhost:8000",
        api_key: str | None = None,
        flush_mode: Literal["immediate", "batch"] = "immediate",
        verify_on_exit: bool = True,
        transport: httpx.BaseTransport | None = None,
    ):
        self.agent_id = agent_id
        self.agent_version = agent_version
        self.input_data = input_data or {}
        self.endpoint = endpoint
        self.api_key = api_key
        self.flush_mode = flush_mode
        self.verify_on_exit = verify_on_exit

        self._client = TraceAIClient(
            endpoint=self.endpoint,
            api_key=self.api_key,
            transport=transport,
        )
        self.session: DecisionSession | None = None
        self.current_sequence: int = 0
        self.last_hash: str | None = None
        self._buffer: list[dict[str, Any]] = []

    @property
    def decision_id(self) -> UUID:
        if self.session is None:
            raise RuntimeError("DecisionContext has not been entered yet.")
        return self.session.id

    def __enter__(self) -> "DecisionContext":
        self.session = self._client.create_decision(
            agent_id=self.agent_id,
            agent_version=self.agent_version,
            input_data=self.input_data,
        )
        self.current_sequence = 1
        self.last_hash = self.session.root_hash
        return self

    def record_event(
        self,
        event_type: str,
        payload: dict[str, Any] | None = None,
        evidence_ids: list[UUID | str] | None = None,
    ) -> AuditEventRecord | None:
        """
        Record an observable agent event into the audit hash chain.
        """
        if self.session is None:
            raise RuntimeError("DecisionContext is not active.")

        payload_clean = payload or {}
        evidence_clean = [str(eid) for eid in (evidence_ids or [])]

        if self.flush_mode == "immediate":
            event = self._client.append_event(
                decision_id=self.session.id,
                event_type=event_type,
                payload=payload_clean,
                evidence_ids=evidence_clean,
            )
            self.current_sequence = event.sequence_number
            self.last_hash = event.event_hash
            return event
        else:
            # Batch mode: buffer locally
            self.current_sequence += 1
            now_iso = datetime.now(timezone.utc).isoformat()
            client_hash = hash_event(
                event_type=event_type,
                timestamp=now_iso,
                payload=payload_clean,
                previous_hash=self.last_hash,
            )
            self.last_hash = client_hash
            self._buffer.append({
                "event_type": event_type,
                "payload": payload_clean,
                "evidence_ids": evidence_clean,
            })
            return None

    def record_evidence(
        self,
        evidence_type: str,
        content: Any,
        metadata: dict[str, Any] | None = None,
        auto_link: bool = True,
        role: str = "retrieved",
    ) -> EvidenceRef:
        """
        Store a snapshot or document in content-addressable storage
        and link it to the current decision.
        """
        if self.session is None:
            raise RuntimeError("DecisionContext is not active.")

        ref = self._client.store_evidence(
            type=evidence_type,
            content=content,
            metadata=metadata,
        )

        if auto_link:
            self._client.link_evidence(
                decision_id=self.session.id,
                evidence_id=ref.id,
                role=role,
            )

        return ref

    def flush(self) -> list[AuditEventRecord]:
        """Flush any buffered events to the backend."""
        if not self._buffer or self.session is None:
            return []

        events = self._client.append_events_batch(
            decision_id=self.session.id,
            events=self._buffer,
        )
        self._buffer.clear()
        if events:
            self.current_sequence = events[-1].sequence_number
            self.last_hash = events[-1].event_hash
        return events

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is None:
                self.record_event(
                    "DECISION_COMPLETED",
                    payload={"status": "completed"},
                )
            else:
                self.record_event(
                    "DECISION_FAILED",
                    payload={
                        "error_type": exc_type.__name__,
                        "error_message": str(exc_val),
                    },
                )

            if self.flush_mode == "batch":
                self.flush()

            if self.verify_on_exit and self.session is not None:
                result: IntegrityCheckResult = self._client.verify_integrity(self.session.id)
                if not result.valid:
                    raise TraceAIIntegrityError(
                        f"Audit chain verification failed for decision {self.session.id}: {result.reason}"
                    )
        finally:
            self._client.close()
