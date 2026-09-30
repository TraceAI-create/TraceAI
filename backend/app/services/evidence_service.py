"""Service for saving, retrieving, and deduplicating evidence files and snapshots."""

import json
import uuid
from sqlalchemy.orm import Session

from app.core.hashing import canonical_json
from app.db.models import Evidence
from app.schemas.evidence import EvidenceCreate
from app.storage import get_storage_provider


def store_evidence(
    db: Session,
    data: EvidenceCreate,
) -> Evidence:
    """Store content in the evidence store and save an index record in the database.

    If the exact same content hash already exists, the existing record is returned
    to avoid storing duplicates.
    """
    # Convert input content into raw bytes and determine content type
    if isinstance(data.content, dict):
        raw_bytes = canonical_json(data.content).encode("utf-8")
        content_type = "application/json"
    elif isinstance(data.content, str):
        raw_bytes = data.content.encode("utf-8")
        content_type = "text/plain"
    elif isinstance(data.content, bytes):
        raw_bytes = data.content
        content_type = "application/octet-stream"
    else:
        raw_bytes = str(data.content).encode("utf-8")
        content_type = "text/plain"

    # Store content in the storage backend
    storage = get_storage_provider()
    content_hash, storage_uri = storage.store(raw_bytes, content_type=content_type)

    # Check if an evidence entry with this content hash already exists
    existing = db.query(Evidence).filter(Evidence.content_hash == content_hash).first()
    if existing:
        return existing

    evidence = Evidence(
        type=data.type,
        content_hash=content_hash,
        storage_uri=storage_uri,
        metadata_json=data.metadata,
    )
    db.add(evidence)
    db.commit()
    db.refresh(evidence)
    return evidence


def get_evidence(
    db: Session,
    evidence_id: uuid.UUID,
) -> Evidence | None:
    """Find an evidence record by its unique ID."""
    return db.get(Evidence, evidence_id)


def get_evidence_by_hash(
    db: Session,
    content_hash: str,
) -> Evidence | None:
    """Find an evidence record by its SHA-256 content hash."""
    return db.query(Evidence).filter(Evidence.content_hash == content_hash).first()


def retrieve_evidence_content(
    db: Session,
    evidence_id: uuid.UUID,
) -> bytes | None:
    """Fetch the raw file content of an evidence item from storage."""
    evidence = db.get(Evidence, evidence_id)
    if not evidence:
        return None

    storage = get_storage_provider()
    return storage.retrieve(evidence.storage_uri)
