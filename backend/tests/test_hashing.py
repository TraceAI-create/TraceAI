from app.core.hashing import canonical_json, hash_event, sha256


def test_canonical_json_key_order():
    # Regardless of dictionary key order, canonical_json must be identical
    d1 = {"b": 2, "a": 1, "c": {"y": 20, "x": 10}}
    d2 = {"c": {"x": 10, "y": 20}, "a": 1, "b": 2}
    assert canonical_json(d1) == canonical_json(d2)


def test_sha256_reproducibility():
    s = "hello traceai"
    assert sha256(s) == sha256(s)
    assert len(sha256(s)) == 64


def test_hash_chaining_deterministic():
    h1 = hash_event(
        event_type="DECISION_CREATED",
        timestamp="2026-09-27T10:00:00+00:00",
        payload={"action": "start"},
        previous_hash=None,
    )
    assert len(h1) == 64

    h2 = hash_event(
        event_type="TOOL_CALL",
        timestamp="2026-09-27T10:00:01+00:00",
        payload={"tool": "search"},
        previous_hash=h1,
    )
    assert len(h2) == 64
    assert h1 != h2
