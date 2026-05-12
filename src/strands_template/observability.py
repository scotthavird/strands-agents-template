"""Observability — console hook provider + optional OpenTelemetry export.

Two pieces:

1. `ConsoleHookProvider` — prints `▶ tool …` / `✓ tool …` lines to stdout
   for every tool call. This is the Strands analog of crewAI's
   `ConsoleListener`. Drop it into `build_agents(hooks=[ConsoleHookProvider()])`.

2. `enable_otel()` — if `OTEL_EXPORTER_OTLP_ENDPOINT` is set, calls
   `StrandsTelemetry().setup_otlp_exporter()`. Wired in `main.py` automatically.
"""
from __future__ import annotations

import os
from typing import Any

from strands import hooks as _hooks


def _resolve_tool_call_events() -> tuple[Any, Any]:
    """Resolve the before/after tool-call event classes across SDK revisions.

    Older revisions exposed `BeforeToolInvocationEvent` / `AfterToolInvocationEvent`;
    current docs show `BeforeToolCallEvent` / `AfterToolCallEvent`. Try both.
    """
    candidates = (
        ("BeforeToolCallEvent", "AfterToolCallEvent"),
        ("BeforeToolInvocationEvent", "AfterToolInvocationEvent"),
    )
    for before, after in candidates:
        before_cls = getattr(_hooks, before, None)
        after_cls = getattr(_hooks, after, None)
        if before_cls is not None and after_cls is not None:
            return before_cls, after_cls
    raise ImportError(
        "Could not find tool-call hook events on `strands.hooks`. "
        "Check your strands-agents version."
    )


class ConsoleHookProvider:
    """Print tool-call lifecycle to stdout. Implements the HookProvider protocol."""

    def register_hooks(self, registry: Any) -> None:
        before_evt, after_evt = _resolve_tool_call_events()
        registry.add_callback(before_evt, self._on_tool_start)
        registry.add_callback(after_evt, self._on_tool_done)

    @staticmethod
    def _tool_name(event: Any) -> str:
        tool_use = getattr(event, "tool_use", None) or {}
        return tool_use.get("name", "?") if isinstance(tool_use, dict) else getattr(tool_use, "name", "?")

    def _on_tool_start(self, event: Any) -> None:
        print(f"▶  {self._tool_name(event)}…", flush=True)

    def _on_tool_done(self, event: Any) -> None:
        result = getattr(event, "result", None)
        size = len(str(result)) if result is not None else 0
        print(f"✓  {self._tool_name(event)}  ({size} chars)", flush=True)


def enable_otel() -> bool:
    """Enable OTLP export when `OTEL_EXPORTER_OTLP_ENDPOINT` is set.

    Returns True if telemetry was started, False otherwise. Safe to call
    repeatedly — Strands' telemetry guards against double-setup.
    """
    if not os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
        return False
    try:
        from strands.telemetry import StrandsTelemetry
    except ImportError:
        print("[observability] strands telemetry not installed — `pip install 'strands-agents[otel]'`")
        return False

    telemetry = StrandsTelemetry()
    telemetry.setup_otlp_exporter()
    return True
