"""API endpoints for storing, retrieving, and downloading evidence artifacts."""

import uuid
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.evidence import EvidenceCreate, EvidenceResponse
from app.services.evidence_service import (
    get_evidence,
    get_evidence_by_hash,
    retrieve_evidence_content,
    store_evidence,
)

router = APIRouter(
    prefix="/api/v1/evidence",
    tags=["evidence"],
)


@router.post(
    "",
    response_model=EvidenceResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_evidence(
    data: EvidenceCreate,
    db: Session = Depends(get_db),
):
    """Store evidence in content-addressable storage and return its metadata."""
    return store_evidence(db, data)


@router.get(
    "/{evidence_id}",
    response_model=EvidenceResponse,
)
def get_evidence_metadata(
    evidence_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """Get metadata for an evidence artifact by its ID."""
    ev = get_evidence(db, evidence_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return ev


@router.get(
    "/hash/{content_hash}",
    response_model=EvidenceResponse,
)
def get_evidence_by_content_hash(
    content_hash: str,
    db: Session = Depends(get_db),
):
    """Get metadata for an evidence artifact using its SHA-256 content hash."""
    ev = get_evidence_by_hash(db, content_hash)
    if not ev:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return ev


@router.get(
    "/{evidence_id}/content",
)
def download_evidence_content(
    evidence_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """Download the raw file or data stored for an evidence artifact."""
    content = retrieve_evidence_content(db, evidence_id)
    if content is None:
        raise HTTPException(status_code=404, detail="Evidence content not found in storage")
    return Response(content=content, media_type="application/octet-stream")
