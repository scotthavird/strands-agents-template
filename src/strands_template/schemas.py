"""Pydantic schemas + the report-shape guardrail.

`AnalysisReport` is what the analyst produces via `agent.structured_output()`.
`ensure_markdown_report` is the editor-side guardrail — equivalent to crewAI's
`guardrail=` function with retries — applied to the final markdown.
"""
from __future__ import annotations

from typing import Callable, Optional

from pydantic import BaseModel, Field


class Finding(BaseModel):
    claim: str = Field(description="One-sentence claim grounded in the research.")
    evidence: str = Field(description="Short quote or paraphrase supporting the claim.")
    source: Optional[str] = Field(default=None, description="URL of the source, if available.")


class AnalysisReport(BaseModel):
    topic: str
    summary: str = Field(description="3-5 sentence synthesis of the research.")
    key_findings: list[Finding] = Field(min_length=3, max_length=10)
    risks: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)


MIN_CHARS = 800
REQUIRED_HEADER_COUNT = 3


def _meets_shape(draft: str) -> tuple[bool, str]:
    if len(draft) < MIN_CHARS:
        return False, f"draft is {len(draft)} chars; need >= {MIN_CHARS}"
    headers = [line for line in draft.splitlines() if line.startswith("## ")]
    if len(headers) < REQUIRED_HEADER_COUNT:
        return False, f"only {len(headers)} `##` headers; need >= {REQUIRED_HEADER_COUNT}"
    return True, ""


def ensure_markdown_report(
    draft: str,
    retry_with: Optional[Callable[[str], str]] = None,
    max_retries: int = 2,
) -> str:
    """Validate the editor's draft. If it fails, ask `retry_with` to rewrite.

    `retry_with` is any callable that takes a feedback prompt and returns the
    rewritten draft as a string. In production this is the editor agent
    wrapped in a tiny lambda; in tests it's a stub.
    """
    current = draft
    for attempt in range(max_retries + 1):
        ok, reason = _meets_shape(current)
        if ok:
            return current
        if retry_with is None or attempt == max_retries:
            raise ValueError(f"report failed shape check after {attempt} retries: {reason}")
        current = retry_with(
            f"Your previous draft failed the shape check ({reason}). "
            f"Rewrite it so it has at least {MIN_CHARS} characters and at "
            f"least {REQUIRED_HEADER_COUNT} `##` section headers. Keep the "
            f"sources and findings intact.\n\nPrevious draft:\n{current}"
        )
    return current
