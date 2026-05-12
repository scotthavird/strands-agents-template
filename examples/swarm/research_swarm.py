#!/usr/bin/env python
"""Swarm variant of the research → analysis → report pipeline.

Same three agents, but coordinated through Strands' Swarm — they hand off
to one another via built-in handoff tools and share working memory. Use
this when you want emergent coordination instead of a fixed topology.

Run inside the container:

    docker compose run --rm agent python examples/swarm/research_swarm.py
"""
from __future__ import annotations

import sys

from strands.multiagent import Swarm

from strands_template.agents import build_agents
from strands_template.observability import ConsoleHookProvider


def main(topic: str) -> None:
    researcher, analyst, editor = build_agents(hooks=[ConsoleHookProvider()])

    swarm = Swarm(
        [researcher, analyst, editor],
        entry_point=researcher,  # type: ignore[call-arg]  # accepted by runtime; type stubs lag
        max_handoffs=10,
        max_iterations=20,
        execution_timeout=600.0,
    )
    result = swarm(f"Research, analyse, and produce a report on: {topic}")
    print("\n— swarm status —", getattr(result, "status", "unknown"))
    print(str(result)[:600])


if __name__ == "__main__":
    topic = sys.argv[1] if len(sys.argv) > 1 else "OpenCV"
    main(topic)
