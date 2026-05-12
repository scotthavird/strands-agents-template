"""Unit tests for the report-shape guardrail — uses a stub editor, no LLM."""
from __future__ import annotations

import pytest

from strands_template.schemas import ensure_markdown_report

_GOOD_DRAFT = (
    "# Report\n\n"
    "## Summary\n" + ("Detailed summary. " * 60) + "\n\n"
    "## Findings\n" + ("Finding line. " * 30) + "\n\n"
    "## Next Steps\nDo more research.\n"
)

_TOO_SHORT = "# tiny\n## one\nshort\n"
_NO_HEADERS = "Lorem ipsum dolor sit amet. " * 60


def test_passes_well_formed():
    out = ensure_markdown_report(_GOOD_DRAFT)
    assert out == _GOOD_DRAFT


def test_rejects_when_no_retry_callable():
    with pytest.raises(ValueError):
        ensure_markdown_report(_TOO_SHORT)


def test_retries_with_callable():
    calls = {"count": 0}

    def stub_editor(_prompt: str) -> str:
        calls["count"] += 1
        return _GOOD_DRAFT

    out = ensure_markdown_report(_TOO_SHORT, retry_with=stub_editor, max_retries=2)
    assert out == _GOOD_DRAFT
    assert calls["count"] == 1


def test_gives_up_after_max_retries():
    def always_short(_prompt: str) -> str:
        return _TOO_SHORT

    with pytest.raises(ValueError):
        ensure_markdown_report(_TOO_SHORT, retry_with=always_short, max_retries=2)


def test_rejects_no_headers():
    with pytest.raises(ValueError):
        ensure_markdown_report(_NO_HEADERS)
