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
    """
    Store content in content-addressable storage (Supabase or local disk)
    and index it in the relational database.
    """
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

    storage = get_storage_provider()
    content_hash, storage_uri = storage.store(raw_bytes, content_type=content_type)

    # Check if this exact content hash already exists
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
    return db.get(Evidence, evidence_id)


def get_evidence_by_hash(
    db: Session,
    content_hash: str,
) -> Evidence | None:
    return db.query(Evidence).filter(Evidence.content_hash == content_hash).first()


def retrieve_evidence_content(
    db: Session,
    evidence_id: uuid.UUID,
) -> bytes | None:
    evidence = db.get(Evidence, evidence_id)
    if not evidence:
        return None

    storage = get_storage_provider()
    return storage.retrieve(evidence.storage_uri)
