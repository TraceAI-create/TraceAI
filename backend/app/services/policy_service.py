"""Service functions for policy registration and querying."""

import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.core.hashing import canonical_json, sha256
from app.db.models import Policy
from app.schemas.policy import PolicyCreate


def create_policy(
    db: Session,
    data: PolicyCreate,
) -> Policy:
    """Create a new policy record and compute the SHA-256 hash of its rules."""
    rules_canonical = canonical_json(data.rules)
    content_hash = sha256(rules_canonical)

    policy = Policy(
        name=data.name,
        version=data.version,
        description=data.description,
        content_hash=content_hash,
        rules=data.rules,
        effective_from=datetime.now(timezone.utc),
        effective_to=data.effective_to,
    )
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


def get_policy(
    db: Session,
    policy_id: uuid.UUID,
) -> Policy | None:
    """Find a policy by its unique ID."""
    return db.get(Policy, policy_id)


def list_policies(
    db: Session,
    active_only: bool = True,
) -> list[Policy]:
    """List policies, optionally filtering to only currently active ones."""
    query = db.query(Policy)
    if active_only:
        now = datetime.now(timezone.utc)
        query = query.filter(
            Policy.effective_from <= now,
            (Policy.effective_to.is_(None)) | (Policy.effective_to >= now),
        )
    return query.order_by(Policy.created_at.desc()).all()
