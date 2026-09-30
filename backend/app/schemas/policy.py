"""Pydantic schemas for policy management and compliance checks."""

import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class PolicyCreate(BaseModel):
    """Payload to create or register a governance policy."""

    name: str = Field(min_length=1)
    version: str = Field(min_length=1)
    description: str | None = None
    rules: dict = Field(default_factory=dict, description="Rules definitions e.g. prohibited_tools, max_budget, pii_filter")
    effective_to: datetime | None = None


class PolicyResponse(BaseModel):
    """Full detail view of a governance policy."""

    id: uuid.UUID
    name: str
    version: str
    description: str | None
    content_hash: str
    storage_uri: str | None
    rules: dict
    effective_from: datetime
    effective_to: datetime | None
    created_at: datetime
