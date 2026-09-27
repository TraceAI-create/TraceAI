import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    reviewer_id: str = Field(min_length=1)
    action: str = Field(pattern="^(approved|rejected|challenged|commented)$")
    comments: str | None = None


class ReviewResponse(BaseModel):
    id: uuid.UUID
    decision_id: uuid.UUID
    reviewer_id: str
    action: str
    comments: str | None
    created_at: datetime
