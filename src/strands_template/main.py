#!/usr/bin/env python
"""Entry points for the Strands template.

Usage (inside the container — `docker compose run --rm agent ...`):

    python -m strands_template.main                # default topic = "OpenCV"
    python -m strands_template.main "Edge AI in 2026"
    strands-template "Edge AI in 2026"             # via the [project.scripts] entry
    strands-chat                                   # interactive REPL with the editor
    strands-replay <session-id>                    # restore a saved chat session

Don't add business logic here — that belongs in `workflow.py` (the sequential
pipeline) or in `examples/{graph,swarm,mcp}/` (the alternative topologies).
"""
from __future__ import annotations

import logging
import sys

from strands_template.observability import enable_otel
from strands_template.workflow import run_workflow

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

enable_otel()


def run() -> str:
    """Run the sequential workflow. Topic from argv[1] (default 'OpenCV')."""
    topic = sys.argv[1] if len(sys.argv) > 1 else "OpenCV"
    logger.info("kickoff topic: %s", topic)
    return run_workflow(topic)


def chat() -> None:
    """Interactive REPL with the editor agent + sliding-window memory + file-backed sessions."""
    from pathlib import Path

    from strands.agent.conversation_manager import SlidingWindowConversationManager
    from strands.session.file_session_manager import FileSessionManager

    from strands_template.agents import build_agents

    sessions_dir = Path(".sessions")
    sessions_dir.mkdir(exist_ok=True)

    session_id = sys.argv[1] if len(sys.argv) > 1 else "default"
    session_manager = FileSessionManager(session_id=session_id, storage_dir=str(sessions_dir))
    conversation_manager = SlidingWindowConversationManager(window_size=20)

    _, _, editor = build_agents()
    editor.conversation_manager = conversation_manager
    editor.session_manager = session_manager

    print(f"strands-chat — session_id={session_id} (Ctrl-D to exit)")
    while True:
        try:
            user = input("\nyou> ").strip()
        except EOFError:
            print()
            return
        if not user:
            continue
        result = editor(user)
        print(f"\neditor> {result}")


def replay() -> None:
    """Restore a chat session by id and continue. Same flag pattern as crewAI's replay."""
    if len(sys.argv) < 2:
        print("usage: strands-replay <session-id>", file=sys.stderr)
        sys.exit(2)
    chat()


if __name__ == "__main__":
    run()
