from fastapi.testclient import TestClient
import pytest
from app.main import app
from traceai_sdk.client import TraceAIClient
from traceai_sdk.context import DecisionContext


@pytest.fixture
def test_transport():
    tc = TestClient(app)
    return tc._transport


def test_client_direct_lifecycle(test_transport):
    client = TraceAIClient(endpoint="http://testserver", transport=test_transport)

    # 1. Create decision
    session = client.create_decision(
        agent_id="test_underwriter",
        agent_version="2.0.0",
        input_data={"loan_id": "L123"},
    )
    assert session.agent_id == "test_underwriter"
    assert session.status == "created"

    # 2. Append event
    ev = client.append_event(
        decision_id=session.id,
        event_type="RULE_EVALUATED",
        payload={"rule": "DTI < 43%", "passed": True},
    )
    assert ev.sequence_number == 2
    assert ev.previous_hash == session.root_hash

    # 3. Store evidence
    ref = client.store_evidence(
        type="tax_return",
        content={"w2_wages": 120000, "year": 2025},
        metadata={"verified": True},
    )
    assert len(ref.content_hash) == 64

    # 4. Link evidence
    client.link_evidence(session.id, ref.id, role="income_verification")

    # 5. Verify integrity
    integrity = client.verify_integrity(session.id)
    assert integrity.valid is True
    assert integrity.event_count == 2
    client.close()


def test_context_manager_immediate_mode(test_transport):
    with DecisionContext(
        agent_id="claim_agent",
        agent_version="1.0.0",
        input_data={"claim_amount": 500},
        endpoint="http://testserver",
        flush_mode="immediate",
        transport=test_transport,
    ) as ctx:
        ctx.record_event("PLAN", {"steps": ["check_coverage", "approve"]})
        ev = ctx.record_evidence(
            evidence_type="policy_doc",
            content={"deductible": 250},
        )
        ctx.record_event("ACTION", {"approved": True}, evidence_ids=[ev.id])

    # Context exited successfully: verify integrity with a fresh client
    client = TraceAIClient(endpoint="http://testserver", transport=test_transport)
    integrity = client.verify_integrity(ctx.decision_id)
    assert integrity.valid is True
    # Initial + PLAN + ACTION + DECISION_COMPLETED = 4 events
    assert integrity.event_count == 4
    client.close()


def test_context_manager_batch_mode(test_transport):
    with DecisionContext(
        agent_id="batch_agent",
        agent_version="1.0.0",
        input_data={"job": "nightly_audit"},
        endpoint="http://testserver",
        flush_mode="batch",
        transport=test_transport,
    ) as ctx:
        ctx.record_event("STEP_1", {"msg": "start"})
        ctx.record_event("STEP_2", {"msg": "processing"})
        ctx.record_event("STEP_3", {"msg": "finish"})

    # Context exit flushes batch: verify integrity
    client = TraceAIClient(endpoint="http://testserver", transport=test_transport)
    integrity = client.verify_integrity(ctx.decision_id)
    assert integrity.valid is True
    # Initial + 3 steps + DECISION_COMPLETED = 5 events
    assert integrity.event_count == 5
    client.close()


def test_context_manager_exception_records_failure(test_transport):
    with pytest.raises(ValueError, match="Simulated agent failure"):
        with DecisionContext(
            agent_id="failing_agent",
            agent_version="1.0.0",
            endpoint="http://testserver",
            transport=test_transport,
        ) as ctx:
            ctx.record_event("STARTED", {"step": 1})
            raise ValueError("Simulated agent failure")

    # Audit chain should STILL be cryptographically valid, with DECISION_FAILED recorded!
    client = TraceAIClient(endpoint="http://testserver", transport=test_transport)
    integrity = client.verify_integrity(ctx.decision_id)
    assert integrity.valid is True
    assert integrity.event_count == 3  # Initial + STARTED + DECISION_FAILED
    client.close()
