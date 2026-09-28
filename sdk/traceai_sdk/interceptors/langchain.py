from typing import Any, Dict, List, Optional
from uuid import UUID

try:
    from langchain_core.callbacks import BaseCallbackHandler
    from langchain_core.outputs import LLMResult
except ImportError:
    class BaseCallbackHandler:  # type: ignore
        """Fallback callback handler base if langchain_core is not installed."""
        pass
    LLMResult = Any  # type: ignore

from traceai_sdk.context import DecisionContext


class TraceAICallbackHandler(BaseCallbackHandler):
    """
    LangChain & LangGraph callback handler that streams events and snapshots
    into an active TraceAI DecisionContext.

    Usage:
        handler = TraceAICallbackHandler(ctx)
        agent_executor.invoke({"input": "..."}, config={"callbacks": [handler]})
    """

    def __init__(self, ctx: DecisionContext, capture_prompts: bool = True):
        super().__init__()
        self.ctx = ctx
        self.capture_prompts = capture_prompts

    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        model_name = (
            (metadata or {}).get("ls_model_name")
            or (serialized or {}).get("name")
            or (serialized or {}).get("id", ["LLM"])[-1]
        )
        payload = {
            "model": str(model_name),
            "run_id": str(run_id),
            "parent_run_id": str(parent_run_id) if parent_run_id else None,
        }
        if self.capture_prompts:
            payload["prompts"] = prompts

        self.ctx.record_event("LLM_INVOCATION_STARTED", payload=payload)

    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        generations = []
        try:
            for gen_list in response.generations:
                for gen in gen_list:
                    generations.append(gen.text)
        except Exception:
            generations = [str(response)]

        llm_output = getattr(response, "llm_output", {}) or {}
        token_usage = llm_output.get("token_usage", {})

        self.ctx.record_event(
            "LLM_INVOCATION_COMPLETED",
            payload={
                "run_id": str(run_id),
                "generations": generations,
                "token_usage": token_usage,
            },
        )

    def on_llm_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        self.ctx.record_event(
            "LLM_INVOCATION_FAILED",
            payload={
                "run_id": str(run_id),
                "error_type": type(error).__name__,
                "error_message": str(error),
            },
        )

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        tool_name = (serialized or {}).get("name") or "tool"
        self.ctx.record_event(
            "TOOL_CALL_STARTED",
            payload={
                "tool_name": tool_name,
                "input": input_str,
                "run_id": str(run_id),
            },
        )

    def on_tool_end(
        self,
        output: Any,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        output_str = str(output)
        evidence_ids = []

        # If output is large (>1KB), store as evidence artifact
        if len(output_str.encode("utf-8")) > 1024:
            ev = self.ctx.record_evidence(
                evidence_type="langchain_tool_output",
                content=output if isinstance(output, (dict, list, str)) else output_str,
                role="tool_result",
            )
            evidence_ids.append(ev.id)
            result_payload = f"[Evidence stored in content-addressable store: {ev.content_hash[:16]}...]"
        else:
            result_payload = output if isinstance(output, (dict, list, str, int, float, bool)) else output_str

        self.ctx.record_event(
            "TOOL_CALL_COMPLETED",
            payload={
                "output": result_payload,
                "run_id": str(run_id),
            },
            evidence_ids=evidence_ids,
        )

    def on_tool_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        self.ctx.record_event(
            "TOOL_CALL_FAILED",
            payload={
                "run_id": str(run_id),
                "error_type": type(error).__name__,
                "error_message": str(error),
            },
        )

    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        chain_name = (serialized or {}).get("name") or (serialized or {}).get("id", ["Chain"])[-1]
        self.ctx.record_event(
            "CHAIN_EXECUTION_STARTED",
            payload={
                "chain_name": str(chain_name),
                "run_id": str(run_id),
            },
        )

    def on_chain_end(
        self,
        outputs: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        self.ctx.record_event(
            "CHAIN_EXECUTION_COMPLETED",
            payload={
                "outputs": outputs,
                "run_id": str(run_id),
            },
        )

    def on_chain_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        self.ctx.record_event(
            "CHAIN_EXECUTION_FAILED",
            payload={
                "run_id": str(run_id),
                "error_type": type(error).__name__,
                "error_message": str(error),
            },
        )
