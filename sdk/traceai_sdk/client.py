"""HTTP client for communicating with the TraceAI Audit API."""

from typing import Any
from uuid import UUID
import httpx

from traceai_sdk.exceptions import TraceAIAPIError
from traceai_sdk.models import AuditEventRecord, DecisionSession, EvidenceRef, IntegrityCheckResult


class TraceAIClient:
    """Client for making HTTP requests to the TraceAI API."""

    def __init__(
        self,
        endpoint: str = "http://localhost:8000",
        api_key: str | None = None,
        timeout: float = 15.0,
        http_client: httpx.Client | None = None,
        transport: httpx.BaseTransport | None = None,
    ):
        self.endpoint = endpoint.rstrip("/")
        self.timeout = timeout
        if http_client is not None:
            self._client = http_client
            self._owns_client = False
        else:
            headers = {"Content-Type": "application/json"}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            self._client = httpx.Client(
                base_url=self.endpoint,
                headers=headers,
                timeout=self.timeout,
                transport=transport,
            )
            self._owns_client = True

    def close(self) -> None:
        """Close the underlying HTTP connection pool if owned by this client."""
        if getattr(self, "_owns_client", True):
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
        """Start a new decision session in TraceAI."""
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
        """Add a single audit event to the decision's audit chain."""
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
        """Add a list of audit events in batch order to the decision's audit chain."""
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
        """Save evidence content in content-addressable storage."""
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
        """Link an existing evidence record to a decision."""
        res = self._client.post(
            f"/api/v1/decisions/{decision_id}/evidence/{evidence_id}",
            params={"role": role},
        )
        if res.status_code != 201:
            raise TraceAIAPIError(f"Failed to link evidence: {res.text}", status_code=res.status_code)

    def verify_integrity(self, decision_id: UUID | str) -> IntegrityCheckResult:
        """Verify the cryptographic audit chain integrity for a decision."""
        res = self._client.get(f"/api/v1/decisions/{decision_id}/integrity")
        if res.status_code != 200:
            raise TraceAIAPIError(f"Failed to check integrity: {res.text}", status_code=res.status_code)
        return IntegrityCheckResult(**res.json())

    def evaluate_policies(
        self,
        decision_id: UUID | str,
        target_payload: dict[str, Any] | None = None,
        policy_id: UUID | str | None = None,
    ) -> dict[str, Any]:
        """Evaluate a decision payload against compliance and governance policies."""
        params = {}
        if policy_id:
            params["policy_id"] = str(policy_id)
        res = self._client.post(
            f"/api/v1/policies/evaluate/{decision_id}",
            json=target_payload or {},
            params=params,
        )
        if res.status_code != 200:
            raise TraceAIAPIError(f"Failed to evaluate policies: {res.text}", status_code=res.status_code)
        return res.json()

    def trigger_replay(
        self,
        decision_id: UUID | str,
        mode: str = "deterministic",
        override_inputs: dict[str, Any] | None = None,
        mock_tools: bool = True,
    ) -> dict[str, Any]:
        """Trigger a sandboxed replay run for a past decision."""
        payload = {
            "mode": mode,
            "override_inputs": override_inputs or {},
            "mock_tools": mock_tools,
        }
        res = self._client.post(f"/api/v1/decisions/{decision_id}/replay", json=payload)
        if res.status_code != 200:
            raise TraceAIAPIError(f"Failed to trigger replay: {res.text}", status_code=res.status_code)
        return res.json()

    def list_replays(self, decision_id: UUID | str) -> list[dict[str, Any]]:
        """List all replay executions completed for a decision."""
        res = self._client.get(f"/api/v1/decisions/{decision_id}/replays")
        if res.status_code != 200:
            raise TraceAIAPIError(f"Failed to list replays: {res.text}", status_code=res.status_code)
        return res.json()

    def get_audit_report(
        self,
        decision_id: UUID | str,
        format: str = "json",
    ) -> dict[str, Any] | str:
        """Download an audit report for a decision in JSON or Markdown format."""
        res = self._client.get(f"/api/v1/decisions/{decision_id}/audit-report", params={"format": format})
        if res.status_code != 200:
            raise TraceAIAPIError(f"Failed to fetch audit report: {res.text}", status_code=res.status_code)
        if format == "markdown":
            return res.text
        return res.json()
