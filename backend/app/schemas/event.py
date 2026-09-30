"""Pydantic schemas for recording and returning audit events."""

import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class EventCreate(BaseModel):
    """Payload to record a single audit event."""

    event_type: str = Field(min_length=1, description="Event type e.g. TOOL_CALL, MODEL_INFERENCE, POLICY_EVALUATION")
    payload: dict = Field(default_factory=dict, description="Event payload data")
    evidence_ids: list[uuid.UUID] = Field(default_factory=list, description="Optional linked evidence IDs")


class BatchEventCreate(BaseModel):
    """Payload to record multiple audit events together in order."""

    events: list[EventCreate] = Field(min_length=1)


class EventDetailResponse(BaseModel):
    """Full detail view of a recorded audit event."""

    id: uuid.UUID
    decision_id: uuid.UUID
    event_type: str
    sequence_number: int
    timestamp: datetime
    payload: dict
    previous_hash: str | None
    event_hash: str
