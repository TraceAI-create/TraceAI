import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class DecisionCreate(BaseModel):
    agent_id: str = Field(min_length=1)
    agent_version: str = Field(min_length=1)
    input_data: dict = Field(default_factory=dict)


class EventResponse(BaseModel):
    id: uuid.UUID
    event_type: str
    sequence_number: int
    timestamp: datetime
    payload: dict
    previous_hash: str | None
    event_hash: str


class DecisionResponse(BaseModel):
    id: uuid.UUID
    agent_id: str
    agent_version: str
    status: str
    input_data: dict
    created_at: datetime
    root_hash: str | None
    events: list[EventResponse]

class IntegrityResponse(BaseModel):
    valid: bool
    event_count: int | None = None
    root_hash: str | None = None
    reason: str | None = None
    event_id: uuid.UUID | None = None
    sequence_number: int | None = None