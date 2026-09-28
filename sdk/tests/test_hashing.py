from app.core.hashing import canonical_json as backend_canonical, hash_event as backend_hash
from traceai_sdk.hashing import canonical_json as sdk_canonical, hash_event as sdk_hash


def test_sdk_and_backend_hashing_parity():
    payload = {
        "user": {"id": 101, "tags": ["admin", "beta"]},
        "timestamp": "2026-09-27T12:00:00Z",
        "nested": {"z": 1, "a": 2},
    }

    # Verify canonical JSON matches between SDK and backend
    assert sdk_canonical(payload) == backend_canonical(payload)

    # Verify event hash matches
    h_sdk = sdk_hash(
        event_type="TOOL_INVOKED",
        timestamp="2026-09-27T12:00:00Z",
        payload=payload,
        previous_hash="0000000000000000000000000000000000000000000000000000000000000000",
    )

    h_backend = backend_hash(
        event_type="TOOL_INVOKED",
        timestamp="2026-09-27T12:00:00Z",
        payload=payload,
        previous_hash="0000000000000000000000000000000000000000000000000000000000000000",
    )

    assert h_sdk == h_backend
