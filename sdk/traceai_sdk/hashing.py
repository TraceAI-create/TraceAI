"""Client-side cryptographic hashing functions matching backend rules."""

import hashlib
import json
from typing import Any


def canonical_json(data: Any) -> str:
    """Convert data into a standard JSON string.

    Sorts dictionary keys and removes extra spaces so the output
    is identical across different systems and programming languages.
    """
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def sha256(data: str) -> str:
    """Return the SHA-256 hash string of the input text."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def hash_event(
    *,
    event_type: str,
    timestamp: str,
    payload: dict,
    previous_hash: str | None,
) -> str:
    """Generate a cryptographic hash for an audit event.

    Includes the previous event's hash to form a tamper-evident audit chain.
    """
    material = {
        "event_type": event_type,
        "timestamp": timestamp,
        "payload": payload,
        "previous_hash": previous_hash,
    }
    return sha256(canonical_json(material))
