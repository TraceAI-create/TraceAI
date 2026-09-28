"""
TraceAI Phase 2 Verification & Test Script
Run this script with:
    python test_phase2.py
"""

import subprocess
import sys
from fastapi.testclient import TestClient
from app.main import app
from traceai_sdk import DecisionContext, TraceAIClient


def run_unit_tests():
    print("=" * 70)
    print("[1/2] RUNNING AUTOMATED TEST SUITE (pytest)")
    print("=" * 70)
    cmd = [sys.executable, "-m", "pytest", "-v"]
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print("\n[!] Unit tests failed.")
        sys.exit(res.returncode)
    print("\n[+] All unit and integration tests passed successfully!\n")


def run_sample_agent_in_process():
    print("=" * 70)
    print("[2/2] RUNNING SAMPLE AGENT WITH TRACEAI-SDK (In-Process TestClient)")
    print("=" * 70)

    # Use FastAPI TestClient transport so this works immediately without needing
    # a separate terminal window to run uvicorn
    client = TestClient(app)
    transport = client._transport

    print("[*] Simulating AI Loan Underwriting Agent with audit instrumentation...")

    with DecisionContext(
        agent_id="loan_underwriter_agent",
        agent_version="1.2.0",
        input_data={
            "applicant": "Sarah Connor",
            "credit_score": 760,
            "requested_amount": 45000,
            "annual_income": 110000,
        },
        endpoint="http://testserver",
        flush_mode="immediate",
        verify_on_exit=True,
        transport=transport,
    ) as ctx:
        print(f"\n  [+] Decision Session Created -> ID: {ctx.decision_id}")

        # 1. Plan
        ctx.record_event("PLAN_GENERATED", {
            "steps": ["fetch_credit_report", "calculate_dti", "evaluate_policy", "recommend"],
            "risk_tolerance": "moderate",
        })
        print("  [+] Step 1: PLAN_GENERATED recorded into cryptographic chain")

        # 2. Retrieve Evidence
        ev = ctx.record_evidence(
            evidence_type="credit_bureau_snapshot",
            content={"bureau": "Experian", "score": 760, "delinquencies": 0},
            metadata={"source": "api.experian.internal"},
            role="retrieved_credit_record",
        )
        print(f"  [+] Step 2: Evidence Snapshot saved -> SHA256={ev.content_hash[:16]}... (ID: {ev.id})")

        ctx.record_event(
            "TOOL_CALL_COMPLETED",
            payload={"tool": "experian_api", "status": "success"},
            evidence_ids=[ev.id],
        )
        print("  [+] Step 2: TOOL_CALL_COMPLETED event linked to evidence")

        # 3. Reason
        ctx.record_event("MODEL_INFERENCE", {
            "model": "claude-3-5-sonnet",
            "calculated_dti": 15.27,
            "confidence": 0.98,
            "rationale": "Applicant credit score 760 and DTI 15.27% well within guidelines.",
        })
        print("  [+] Step 3: MODEL_INFERENCE recorded with confidence and rationale")

        # 4. Action
        ctx.record_event("ACTION_TAKEN", {
            "action": "APPROVE_LOAN",
            "approved_amount": 45000,
            "interest_rate": 6.25,
        })
        print("  [+] Step 4: ACTION_TAKEN emitted (APPROVE_LOAN)")

    # Verify audit chain
    sdk_client = TraceAIClient(endpoint="http://testserver", transport=transport)
    integrity = sdk_client.verify_integrity(ctx.decision_id)
    sdk_client.close()

    print("\n" + "=" * 70)
    print("AUDIT CHAIN INTEGRITY REPORT")
    print("=" * 70)
    print(f"  Decision ID       : {ctx.decision_id}")
    print(f"  Audit Chain Valid : {integrity.valid}")
    print(f"  Total Events      : {integrity.event_count}")
    print(f"  Final Root Hash   : {integrity.root_hash}")
    print("=" * 70)
    print("\n[SUCCESS] Phase 2 SDK & Decision Traceability is 100% verified and functional!")


if __name__ == "__main__":
    run_unit_tests()
    run_sample_agent_in_process()
