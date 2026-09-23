import hashlib
import json
from typing import Any


def canonical_json(data: Any) -> str:
    """
    Convert data into a deterministic JSON representation.

    The same logical data must always produce the same byte sequence.
    """
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def sha256(data: str) -> str:
    """Return the SHA-256 hex digest of a string."""
    return hashlib.sha256(
        data.encode("utf-8")
    ).hexdigest()


def hash_event(
    *,
    event_type: str,
    timestamp: str,
    payload: dict,
    previous_hash: str | None,
) -> str:
    """
    Generate the cryptographic hash for an audit event.

    The previous event hash is included so that events form
    a tamper-evident hash chain.
    """
    material = {
        "event_type": event_type,
        "timestamp": timestamp,
        "payload": payload,
        "previous_hash": previous_hash,
    }

    return sha256(canonical_json(material))