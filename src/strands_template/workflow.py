"""Sequential research → analysis → report workflow.

This is the simplest of three orchestration patterns shipped with the
template. The Graph variant lives in `examples/graph/research_graph.py`
and the Swarm variant in `examples/swarm/research_swarm.py` — same three
agents, different topology.
"""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from strands_template.agents import build_agents
from strands_template.observability import ConsoleHookProvider
from strands_template.schemas import AnalysisReport, ensure_markdown_report

logger = logging.getLogger(__name__)


def _load_tasks() -> dict:
    return yaml.safe_load((Path(__file__).parent / "config" / "tasks.yaml").read_text())


def _agent_text(result: Any) -> str:
    """Extract the text response from an Agent invocation result.

    Strands' AgentResult exposes `.message` (a dict in the Anthropic
    message shape) and a `__str__` that yields the concatenated text.
    Use the str fallback to stay compatible across SDK revisions.
    """
    message = getattr(result, "message", None)
    if isinstance(message, dict):
        parts = [c.get("text", "") for c in message.get("content", []) if isinstance(c, dict)]
        joined = "\n".join(p for p in parts if p)
        if joined:
            return joined
    if isinstance(message, str) and message.strip():
        return message
    return str(result)


def run_workflow(topic: str, *, write_report: bool = True) -> str:
    """Run the full pipeline. Returns the final markdown report.

    `write_report=True` writes `report.md` in the current working dir.
    """
    tasks = _load_tasks()
    current_year = str(datetime.now().year)

    researcher, analyst, editor = build_agents(hooks=[ConsoleHookProvider()])

    logger.info("research_task: %s", topic)
    research_prompt = tasks["research_task"]["description"].format(
        topic=topic, current_year=current_year
    )
    research_result = researcher(research_prompt)
    findings = _agent_text(research_result)

    logger.info("analysis_task")
    analysis_prompt = (
        f"{tasks['analysis_task']['description']}\n\n"
        f"Topic: {topic}\n\nResearch brief:\n{findings}"
    )
    report: AnalysisReport = analyst.structured_output(AnalysisReport, analysis_prompt)

    logger.info("report_task")
    report_prompt = (
        f"{tasks['report_task']['description']}\n\n"
        f"Topic: {topic}\n\n"
        f"Structured analysis:\n{report.model_dump_json(indent=2)}\n\n"
        f"Raw research (for sources / extra detail):\n{findings}"
    )

    def _editor_call(prompt: str) -> str:
        return _agent_text(editor(prompt))

    draft = _editor_call(report_prompt)
    final = ensure_markdown_report(draft, retry_with=_editor_call, max_retries=2)

    if write_report:
        Path("report.md").write_text(final)
        print(f"\n— wrote {len(final)} chars to report.md\n")
    return final
