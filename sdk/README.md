# TraceAI Python SDK (`traceai-sdk`)

Lightweight, tamper-evident audit and instrumentation SDK for AI agents (LangGraph, LangChain, or custom agent frameworks).

## Key Features
- **Deterministic Chained Hashing**: Generates SHA-256 hash chains locally for every step.
- **Evidence Snapshots**: Automatically stores large documents, raw prompts, and API responses in content-addressable storage.
- **Scoped Context**: Simple `DecisionContext` context manager capturing agent lifecycles (`PLAN`, `RETRIEVAL`, `REASONING`, `ACTION`).
- **Cryptographic Verification**: Auto-verifies decision root hashes against the TraceAI platform.

## Quickstart

```python
from traceai_sdk import DecisionContext

with DecisionContext(
    agent_id="credit_risk_agent",
    agent_version="1.0.0",
    input_data={"applicant_id": "app_1001", "requested_amount": 50000},
    endpoint="http://localhost:8000",
) as ctx:
    # 1. Plan
    ctx.record_event("PLAN_GENERATED", {"steps": ["check_credit", "decide"]})

    # 2. Retrieve Evidence
    ev = ctx.record_evidence(
        evidence_type="credit_report",
        content={"bureau": "Equifax", "score": 750},
    )
    ctx.record_event("EVIDENCE_RETRIEVED", {"source": "credit_bureau"}, evidence_ids=[ev.id])

    # 3. Reason
    ctx.record_event("REASONING_COMPLETED", {"rationale": "Score exceeds 700 threshold"})

    # 4. Action
    ctx.record_event("ACTION_TAKEN", {"action": "APPROVE_LOAN"})
```
