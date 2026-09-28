import asyncio
import functools
import inspect
import time
from typing import Any, Callable
from uuid import UUID

from traceai_sdk.context import DecisionContext


def instrument_tool(
    name: str | None = None,
    description: str | None = None,
    snapshot_threshold_bytes: int = 1024,
    snapshot: bool = False,
    role: str = "tool_output",
):
    """
    Decorator to instrument any tool, function, or API call.
    Automatically captures arguments, latency, return values, errors,
    and creates content-addressable evidence snapshots for large outputs.

    Usage:
        @instrument_tool(name="fetch_credit_score", snapshot=True)
        def get_credit_score(user_id: str, bureau: str = "Experian"):
            ...
    """

    def decorator(func: Callable):
        tool_name = name or func.__name__

        if inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                ctx = _get_active_context()
                start_time = time.perf_counter()
                call_args = _extract_args(func, args, kwargs)

                if ctx:
                    ctx.record_event(
                        "TOOL_CALL_STARTED",
                        payload={"tool_name": tool_name, "arguments": call_args},
                    )

                try:
                    result = await func(*args, **kwargs)
                    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
                    _record_completion(ctx, tool_name, call_args, result, latency_ms, snapshot, snapshot_threshold_bytes, role)
                    return result
                except Exception as exc:
                    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
                    _record_failure(ctx, tool_name, call_args, exc, latency_ms)
                    raise

            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                ctx = _get_active_context()
                start_time = time.perf_counter()
                call_args = _extract_args(func, args, kwargs)

                if ctx:
                    ctx.record_event(
                        "TOOL_CALL_STARTED",
                        payload={"tool_name": tool_name, "arguments": call_args},
                    )

                try:
                    result = func(*args, **kwargs)
                    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
                    _record_completion(ctx, tool_name, call_args, result, latency_ms, snapshot, snapshot_threshold_bytes, role)
                    return result
                except Exception as exc:
                    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
                    _record_failure(ctx, tool_name, call_args, exc, latency_ms)
                    raise

            return sync_wrapper

    return decorator


# Context registry so decorated tools can automatically discover the enclosing DecisionContext
_active_context_stack: list[DecisionContext] = []


def _get_active_context() -> DecisionContext | None:
    return _active_context_stack[-1] if _active_context_stack else None


def set_active_context(ctx: DecisionContext) -> None:
    _active_context_stack.append(ctx)


def clear_active_context(ctx: DecisionContext) -> None:
    if ctx in _active_context_stack:
        _active_context_stack.remove(ctx)


def _extract_args(func: Callable, args: tuple, kwargs: dict) -> dict[str, Any]:
    try:
        sig = inspect.signature(func)
        bound = sig.bind_partial(*args, **kwargs)
        bound.apply_defaults()
        clean = {}
        for k, v in bound.arguments.items():
            # Don't capture self or cls
            if k in ("self", "cls"):
                continue
            if isinstance(v, (str, int, float, bool, list, dict, type(None))):
                clean[k] = v
            else:
                clean[k] = str(v)
        return clean
    except Exception:
        return {"args": [str(a) for a in args], "kwargs": {k: str(v) for k, v in kwargs.items()}}


def _record_completion(
    ctx: DecisionContext | None,
    tool_name: str,
    call_args: dict,
    result: Any,
    latency_ms: float,
    snapshot: bool,
    snapshot_threshold_bytes: int,
    role: str,
) -> None:
    if ctx is None:
        return

    evidence_ids: list[UUID] = []
    result_str = str(result)
    is_large = len(result_str.encode("utf-8")) > snapshot_threshold_bytes

    if snapshot or is_large:
        # Offload output to Evidence Store
        ev = ctx.record_evidence(
            evidence_type=f"tool_output_{tool_name}",
            content=result if isinstance(result, (dict, list, str)) else result_str,
            metadata={"tool_name": tool_name, "latency_ms": latency_ms},
            auto_link=True,
            role=role,
        )
        evidence_ids.append(ev.id)
        payload_result = f"[Evidence stored in content-addressable store: {ev.content_hash[:16]}...]"
    else:
        payload_result = result if isinstance(result, (dict, list, str, int, float, bool)) else result_str

    ctx.record_event(
        "TOOL_CALL_COMPLETED",
        payload={
            "tool_name": tool_name,
            "arguments": call_args,
            "result": payload_result,
            "latency_ms": latency_ms,
        },
        evidence_ids=evidence_ids,
    )


def _record_failure(
    ctx: DecisionContext | None,
    tool_name: str,
    call_args: dict,
    exc: Exception,
    latency_ms: float,
) -> None:
    if ctx is None:
        return

    ctx.record_event(
        "TOOL_CALL_FAILED",
        payload={
            "tool_name": tool_name,
            "arguments": call_args,
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "latency_ms": latency_ms,
        },
    )
