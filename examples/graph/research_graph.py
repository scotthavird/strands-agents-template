#!/usr/bin/env python
"""Graph variant of the research → analysis → report pipeline.

Same three agents as the sequential workflow, wired through `GraphBuilder`.
Demonstrates a conditional edge: the editor node only runs if the analyst's
output passes a small confidence check.

Run inside the container:

    docker compose run --rm agent python examples/graph/research_graph.py
"""
from __future__ import annotations

import sys

from strands.multiagent import GraphBuilder

from strands_template.agents import build_agents
from strands_template.observability import ConsoleHookProvider


def _analysis_is_strong(state) -> bool:
    """Conditional edge predicate: only run the editor on substantial output."""
    text = str(getattr(state, "result", "") or state)
    return len(text) > 400


def main(topic: str) -> None:
    researcher, analyst, editor = build_agents(hooks=[ConsoleHookProvider()])

    builder = GraphBuilder()
    builder.add_node(researcher, "research")
    builder.add_node(analyst, "analysis")
    builder.add_node(editor, "report")
    builder.add_edge("research", "analysis")
    builder.add_edge("analysis", "report", condition=_analysis_is_strong)
    builder.set_entry_point("research")

    graph = builder.build()
    result = graph(f"Research, analyse, and report on: {topic}")
    print("\n— graph status —", getattr(result, "status", "unknown"))
    print(str(result)[:600])


if __name__ == "__main__":
    topic = sys.argv[1] if len(sys.argv) > 1 else "OpenCV"
    main(topic)
