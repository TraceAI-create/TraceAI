import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class EventCreate(BaseModel):
    event_type: str = Field(min_length=1, description="Event type e.g. TOOL_CALL, MODEL_INFERENCE, POLICY_EVALUATION")
    payload: dict = Field(default_factory=dict, description="Event payload data")
    evidence_ids: list[uuid.UUID] = Field(default_factory=list, description="Optional linked evidence IDs")


class BatchEventCreate(BaseModel):
    events: list[EventCreate] = Field(min_length=1)


class EventDetailResponse(BaseModel):
    id: uuid.UUID
    decision_id: uuid.UUID
    event_type: str
    sequence_number: int
    timestamp: datetime
    payload: dict
    previous_hash: str | None
    event_hash: str
