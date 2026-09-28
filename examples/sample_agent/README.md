# Sample Agent: Loan Underwriting & Risk Assessment

This example demonstrates how an AI agent uses the `traceai-sdk` to produce an end-to-end tamper-evident audit trail following the 4 core steps:
1. **Plan**: Formulate the execution steps and risk bounds.
2. **Retrieve Evidence**: Fetch and snapshot third-party data (e.g. credit bureau reports) into the Content-Addressable Evidence Store.
3. **Reason**: Log LLM reasoning, calculated metrics (DTI), and confidence scores.
4. **Take Action**: Execute the recommendation with an immutable audit hash chain.

## Running the Example

1. **Start the TraceAI Backend API**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

2. **Run the Agent**:
   ```bash
   python examples/sample_agent/agent.py --applicant "Sarah Connor" --score 760 --amount 45000
   ```
