"""
Sample Agent: Loan Underwriting & Risk Assessment
Demonstrating TraceAI Audit SDK instrumentation:
Plan -> Retrieve Evidence -> Reason -> Take Action
"""

import argparse
import sys
import time
from traceai_sdk import DecisionContext, TraceAIClient


def run_loan_agent(
    applicant_name: str = "Sarah Connor",
    credit_score: int = 760,
    requested_amount: int = 45000,
    annual_income: int = 110000,
    endpoint: str = "http://localhost:8000",
):
    print("=" * 60)
    print(f"[*] Starting Loan Underwriting Agent for {applicant_name}")
    print(f"[*] Connecting to TraceAI Audit System at: {endpoint}")
    print("=" * 60)

    input_payload = {
        "applicant": applicant_name,
        "credit_score": credit_score,
        "requested_amount": requested_amount,
        "annual_income": annual_income,
    }

    with DecisionContext(
        agent_id="loan_underwriter_agent",
        agent_version="1.2.0",
        input_data=input_payload,
        endpoint=endpoint,
        flush_mode="immediate",
        verify_on_exit=True,
    ) as ctx:
        print(f"\n[+] Decision session created. ID: {ctx.decision_id}")

        # ---------------------------------------------------------
        # STEP 1: PLAN
        # ---------------------------------------------------------
        print("\n--- [Step 1: Planning Execution] ---")
        plan_data = {
            "steps": [
                "fetch_credit_report",
                "calculate_debt_to_income",
                "evaluate_underwriting_policy",
                "generate_recommendation",
            ],
            "max_risk_tolerance": "moderate",
        }
        ctx.record_event("PLAN_GENERATED", plan_data)
        print("  -> Plan recorded in audit chain.")
        time.sleep(0.5)

        # ---------------------------------------------------------
        # STEP 2: RETRIEVE EVIDENCE
        # ---------------------------------------------------------
        print("\n--- [Step 2: Retrieving Evidence Snapshots] ---")
        bureau_report = {
            "bureau": "Experian",
            "score": credit_score,
            "open_lines": 6,
            "delinquencies": 0,
            "oldest_account_years": 12,
            "monthly_debt_obligations": 1400,
        }
        ev_report = ctx.record_evidence(
            evidence_type="credit_bureau_snapshot",
            content=bureau_report,
            metadata={"source": "api.experian.internal", "timestamp": "2026-09-27T12:00:00Z"},
            role="retrieved_credit_record",
        )
        print(f"  -> Evidence stored in Content-Addressable Store: SHA256={ev_report.content_hash[:16]}...")

        ctx.record_event(
            "TOOL_CALL_COMPLETED",
            payload={"tool": "experian_api", "status_code": 200, "bureau": "Experian"},
            evidence_ids=[ev_report.id],
        )
        print(f"  -> Event linked to evidence artifact {ev_report.id}")
        time.sleep(0.5)

        # ---------------------------------------------------------
        # STEP 3: REASON (LLM Inference Simulation)
        # ---------------------------------------------------------
        print("\n--- [Step 3: Reasoning & Policy Evaluation] ---")
        monthly_income = annual_income / 12
        monthly_debt = bureau_report["monthly_debt_obligations"]
        dti_ratio = round((monthly_debt / monthly_income) * 100, 2)

        reasoning_payload = {
            "model": "claude-3-5-sonnet",
            "calculated_dti_percent": dti_ratio,
            "dti_threshold": 43.0,
            "credit_score_threshold": 680,
            "rationale": (
                f"Applicant credit score {credit_score} is well above threshold (680). "
                f"DTI ratio is {dti_ratio}%, below maximum allowable 43.0%. "
                f"Requested amount ${requested_amount:,} is within income parameters."
            ),
            "confidence_score": 0.98,
        }
        ctx.record_event("MODEL_INFERENCE", reasoning_payload)
        print(f"  -> Reasoning logged: DTI={dti_ratio}%, Confidence={reasoning_payload['confidence_score']}")
        time.sleep(0.5)

        # ---------------------------------------------------------
        # STEP 4: TAKE ACTION
        # ---------------------------------------------------------
        print("\n--- [Step 4: Executing Final Action] ---")
        action_payload = {
            "action": "APPROVE_LOAN",
            "approved_amount": requested_amount,
            "interest_rate_percent": 6.25,
            "amortization_months": 36,
            "stipulations": ["Submit proof of employment prior to disbursement"],
        }
        ctx.record_event("ACTION_TAKEN", action_payload)
        print(f"  -> Action taken: {action_payload['action']} (${action_payload['approved_amount']:,})")

    # Outside the context manager: DecisionContext has logged DECISION_COMPLETED and verified integrity
    print("\n" + "=" * 60)
    print("[*] Verifying Decision Cryptographic Audit Trail...")
    client = TraceAIClient(endpoint=endpoint)
    try:
        integrity = client.verify_integrity(ctx.decision_id)
        print(f"  -> Audit Chain Valid: {integrity.valid}")
        print(f"  -> Total Events Chained: {integrity.event_count}")
        print(f"  -> Final Decision Root Hash: {integrity.root_hash}")
        print("=" * 60)
        print("[SUCCESS] Agent decision fully captured, hashed, and verified!")
    finally:
        client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run TraceAI Sample Underwriting Agent")
    parser.add_argument("--endpoint", default="http://localhost:8000", help="TraceAI API endpoint")
    parser.add_argument("--applicant", default="Sarah Connor", help="Applicant name")
    parser.add_argument("--score", type=int, default=760, help="Credit score")
    parser.add_argument("--amount", type=int, default=45000, help="Requested loan amount")
    parser.add_argument("--income", type=int, default=110000, help="Annual income")
    args = parser.parse_args()

    run_loan_agent(
        applicant_name=args.applicant,
        credit_score=args.score,
        requested_amount=args.amount,
        annual_income=args.income,
        endpoint=args.endpoint,
    )
