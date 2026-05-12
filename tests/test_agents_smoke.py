"""Smoke test — verifies the three agents assemble without an LLM call.

The integration test variant is gated by RUN_INTEGRATION=1 plus a real
provider key.
"""
from __future__ import annotations

import os

import pytest


def test_agents_assemble(monkeypatch):
    """Build all three agents without invoking — catches wiring/import regressions."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-real")

    from strands_template.agents import build_agents

    researcher, analyst, editor = build_agents()
    for agent, expected_name in [(researcher, "researcher"), (analyst, "analyst"), (editor, "editor")]:
        assert agent is not None
        assert getattr(agent, "name", expected_name) == expected_name
        assert getattr(agent, "system_prompt", "")
    assert len(getattr(researcher, "tool_names", []) or researcher.tool_registry.registry) >= 1


def test_workflow_imports():
    """`run_workflow` is importable and has the expected signature."""
    from inspect import signature

    from strands_template.workflow import run_workflow

    sig = signature(run_workflow)
    assert "topic" in sig.parameters


@pytest.mark.integration
@pytest.mark.skipif(
    os.getenv("RUN_INTEGRATION") != "1"
    or not (os.getenv("ANTHROPIC_API_KEY") or os.getenv("AWS_ACCESS_KEY_ID") or os.getenv("AWS_BEARER_TOKEN_BEDROCK")),
    reason="set RUN_INTEGRATION=1 plus a provider key to run this test",
)
def test_full_workflow_produces_report():
    from strands_template.workflow import run_workflow

    final = run_workflow("OpenCV", write_report=False)
    assert isinstance(final, str)
    assert len(final) > 200
