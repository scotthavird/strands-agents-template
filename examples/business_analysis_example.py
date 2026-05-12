#!/usr/bin/env python
"""Pre-baked business-analysis workflow run.

Same sequential pipeline as `python -m strands_template.main`, but with a
domain-specific topic and focus areas hard-coded so engineers can see what
'real' input shapes look like.

Run inside the container:

    docker compose run --rm agent python examples/business_analysis_example.py
"""
from __future__ import annotations

from datetime import datetime

from strands_template.workflow import run_workflow


def main() -> None:
    topic = (
        "Electric Vehicle Market Trends in {year} — adoption barriers, "
        "key players, charging infrastructure, and policy tailwinds"
    ).format(year=datetime.now().year)
    print(f"running business-analysis workflow on: {topic}\n")
    final = run_workflow(topic)
    print("\n— final report (first 400 chars) —")
    print(final[:400] + ("…" if len(final) > 400 else ""))


if __name__ == "__main__":
    main()
