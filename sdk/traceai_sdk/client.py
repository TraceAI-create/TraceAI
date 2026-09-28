from typing import Any
from uuid import UUID
import httpx

from traceai_sdk.exceptions import TraceAIAPIError
from traceai_sdk.models import AuditEventRecord, DecisionSession, EvidenceRef, IntegrityCheckResult


class TraceAIClient:
    """
    HTTP client for the TraceAI Audit API.
    """

    def __init__(
        self,
        endpoint: str = "http://localhost:8000",
        api_key: str | None = None,
        timeout: float = 15.0,
        transport: httpx.BaseTransport | None = None,
    ):
        self.endpoint = endpoint.rstrip("/")
        self.timeout = timeout
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self._client = httpx.Client(
            base_url=self.endpoint,
            headers=headers,
            timeout=self.timeout,
            transport=transport,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def create_decision(
        self,
        agent_id: str,
        agent_version: str,
        input_data: dict[str, Any] | None = None,
    ) -> DecisionSession:
        payload = {
            "agent_id": agent_id,
            "agent_version": agent_version,
            "input_data": input_data or {},
        }
        res = self._client.post("/api/v1/decisions", json=payload)
        if res.status_code != 201:
            raise TraceAIAPIError(f"Failed to create decision: {res.text}", status_code=res.status_code)
        data = res.json()
        return DecisionSession(**data)

    def append_event(
        self,
        decision_id: UUID | str,
        event_type: str,
        payload: dict[str, Any] | None = None,
        evidence_ids: list[UUID | str] | None = None,
    ) -> AuditEventRecord:
        body = {
            "event_type": event_type,
            "payload": payload or {},
            "evidence_ids": [str(eid) for eid in (evidence_ids or [])],
        }
        res = self._client.post(f"/api/v1/decisions/{decision_id}/events", json=body)
        if res.status_code != 201:
            raise TraceAIAPIError(f"Failed to append event: {res.text}", status_code=res.status_code)
        return AuditEventRecord(**res.json())

    def append_events_batch(
        self,
        decision_id: UUID | str,
        events: list[dict[str, Any]],
    ) -> list[AuditEventRecord]:
        formatted_events = []
        for ev in events:
            formatted_events.append({
                "event_type": ev["event_type"],
                "payload": ev.get("payload", {}),
                "evidence_ids": [str(eid) for eid in ev.get("evidence_ids", [])],
            })
        body = {"events": formatted_events}
        res = self._client.post(f"/api/v1/decisions/{decision_id}/events/batch", json=body)
        if res.status_code != 201:
            raise TraceAIAPIError(f"Failed to append batch events: {res.text}", status_code=res.status_code)
        return [AuditEventRecord(**item) for item in res.json()]

    def store_evidence(
        self,
        type: str,
        content: Any,
        metadata: dict[str, Any] | None = None,
    ) -> EvidenceRef:
        body = {
            "type": type,
            "content": content,
            "metadata": metadata or {},
        }
        res = self._client.post("/api/v1/evidence", json=body)
        if res.status_code != 201:
            raise TraceAIAPIError(f"Failed to store evidence: {res.text}", status_code=res.status_code)
        return EvidenceRef(**res.json())

    def link_evidence(
        self,
        decision_id: UUID | str,
        evidence_id: UUID | str,
        role: str = "context",
    ) -> None:
        res = self._client.post(
            f"/api/v1/decisions/{decision_id}/evidence/{evidence_id}",
            params={"role": role},
        )
        if res.status_code != 201:
            raise TraceAIAPIError(f"Failed to link evidence: {res.text}", status_code=res.status_code)

    def verify_integrity(self, decision_id: UUID | str) -> IntegrityCheckResult:
        res = self._client.get(f"/api/v1/decisions/{decision_id}/integrity")
        if res.status_code != 200:
            raise TraceAIAPIError(f"Failed to check integrity: {res.text}", status_code=res.status_code)
        return IntegrityCheckResult(**res.json())
