import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class EvidenceCreate(BaseModel):
    type: str = Field(description="Type of evidence e.g. document, api_response, model_output, snapshot")
    content: str | dict = Field(description="Raw text or JSON payload to store in content-addressable storage")
    metadata: dict = Field(default_factory=dict, description="Arbitrary metadata e.g. source, mime_type")


class EvidenceResponse(BaseModel):
    id: uuid.UUID
    type: str
    content_hash: str
    storage_uri: str
    metadata_json: dict
    created_at: datetime


class DecisionEvidenceLink(BaseModel):
    decision_id: uuid.UUID
    evidence_id: uuid.UUID
    role: str = "context"
    created_at: datetime
