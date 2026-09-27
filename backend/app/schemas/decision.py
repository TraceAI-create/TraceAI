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


class EvidenceLinkResponse(BaseModel):
    id: uuid.UUID
    evidence_id: uuid.UUID
    role: str
    created_at: datetime


class ReviewActionResponse(BaseModel):
    id: uuid.UUID
    reviewer_id: str
    action: str
    comments: str | None
    created_at: datetime


class DecisionSummaryResponse(BaseModel):
    id: uuid.UUID
    agent_id: str
    agent_version: str
    status: str
    created_at: datetime
    root_hash: str | None
    event_count: int = 0


class DecisionResponse(BaseModel):
    id: uuid.UUID
    agent_id: str
    agent_version: str
    status: str
    input_data: dict
    created_at: datetime
    root_hash: str | None
    events: list[EventResponse] = []
    evidence_links: list[EvidenceLinkResponse] = []
    review_actions: list[ReviewActionResponse] = []


class IntegrityResponse(BaseModel):
    valid: bool
    event_count: int | None = None
    root_hash: str | None = None
    reason: str | None = None
    event_id: uuid.UUID | None = None
    sequence_number: int | None = None