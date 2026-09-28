from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, Field


class DecisionSession(BaseModel):
    id: UUID
    agent_id: str
    agent_version: str
    status: str
    input_data: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    root_hash: str | None = None


class AuditEventRecord(BaseModel):
    id: UUID
    decision_id: UUID
    event_type: str
    sequence_number: int
    timestamp: datetime
    payload: dict[str, Any]
    previous_hash: str | None
    event_hash: str


class EvidenceRef(BaseModel):
    id: UUID
    type: str
    content_hash: str
    storage_uri: str
    metadata_json: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class IntegrityCheckResult(BaseModel):
    valid: bool
    event_count: int | None = None
    root_hash: str | None = None
    reason: str | None = None
    sequence_number: int | None = None
