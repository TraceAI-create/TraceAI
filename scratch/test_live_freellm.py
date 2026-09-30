"""Test script for running a live AI decision with FreeLLMAPI, replay, and audit reporting."""

import os
import requests
from langchain_openai import ChatOpenAI
from traceai_sdk import DecisionContext, instrument_tool
from traceai_sdk.interceptors.langchain import TraceAICallbackHandler


# 1. Define an instrumented tool
@instrument_tool(name="check_credit_score")
def check_credit_score(applicant_id: str) -> dict:
    """Check credit score and account details for an applicant."""
    return {
        "applicant_id": applicant_id,
        "score": 755,
        "tier": "PRIME",
        "existing_debt": 1200,
    }


# 2. Configure FreeLLMAPI client
llm = ChatOpenAI(
    model="gemini-3.1-flash-lite",
    openai_api_key=os.environ.get("FREELLMAPI_KEY"),
    openai_api_base="http://127.0.0.1:31415/v1",
    temperature=0.2,
)

print("\n--- 1. Recording Live AI Decision via FreeLLMAPI ---")
with DecisionContext(
    agent_id="loan-approval-agent",
    agent_version="1.0.0",
    input_data={"applicant": "cust_9821", "loan_amount": 35000},
    endpoint="http://127.0.0.1:8000",
) as ctx:
    # Callback handler records prompts, latency, and model outputs into the decision context
    handler = TraceAICallbackHandler(ctx)

    # Tool call captured automatically by @instrument_tool
    applicant_data = check_credit_score("cust_9821")

    prompt = (
        f"You are a loan underwriter. Review applicant {applicant_data['applicant_id']} "
        f"with credit score {applicant_data['score']} ({applicant_data['tier']}) and existing debt ${applicant_data['existing_debt']}. "
        f"Loan requested: $35,000. Give your decision: APPROVED or REJECTED, and state 1 sentence rationale."
    )

    response = llm.invoke(prompt, config={"callbacks": [handler]})
    print(f"\nLive LLM Response:\n{response.content}\n")

    ctx.record_event(
        event_type="OUTPUT",
        payload={
            "verdict": "APPROVED" if "APPROVED" in response.content else "REJECTED",
            "rationale": response.content,
        },
    )

decision_id = str(ctx.decision_id)
print(f"Decision saved with ID: {decision_id}")

# 3. Trigger deterministic replay and comparison
print("\n--- 2. Triggering Replay & Comparison ---")
replay_res = requests.post(
    f"http://127.0.0.1:8000/api/v1/decisions/{decision_id}/replay",
    json={
        "mode": "deterministic",
        "mock_tool_responses": True,
    },
)
print("Replay HTTP Status:", replay_res.status_code)
replay_data = replay_res.json()
print("Replay Status:", replay_data.get("status"))
print("Similarity Score:", replay_data.get("similarity_score"))
print("Diff Summary:", replay_data.get("diff_summary"))

# 4. Fetch full compliance audit report
print("\n--- 3. Fetching Full Compliance Audit Report ---")
report_res = requests.get(
    f"http://127.0.0.1:8000/api/v1/decisions/{decision_id}/audit-report?format=markdown",
)
print("Report HTTP Status:", report_res.status_code)
if report_res.status_code == 200:
    print("\n" + "=" * 50 + " AUDIT REPORT " + "=" * 50)
    print(report_res.text)
    print("=" * 114)
else:
    print(report_res.text)
