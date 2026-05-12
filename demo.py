#!/usr/bin/env python
"""Strands Template Demo
======================

Interactive demo showcasing several use cases on the same three agents.

Usage (Docker):
    docker compose run --rm agent python demo.py
"""
from __future__ import annotations

import os
import sys
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

try:
    from strands_template.workflow import run_workflow
except ImportError:
    print("❌ Error: Could not import strands_template. Are you in the project root?")
    print("💡 Run inside the container: docker compose run --rm agent python demo.py")
    sys.exit(1)


def print_header():
    print(
        """
🚀 ===================================================== 🚀

   Strands Agents Template — Interactive Demo
   Three agents collaborating: research → analysis → report

🤖 ===================================================== 🤖
"""
    )


def show_menu():
    print("🎯 Choose a research topic:")
    print()
    print("1. 🔬 Technology Research (OpenCV)")
    print("2. 📊 Market Analysis (Electric Vehicles)")
    print("3. 🏢 Business Intelligence (AI Startups)")
    print("4. 🎨 Content Strategy (B2B SaaS)")
    print("5. 🔧 Technical Analysis (Cloud Architecture)")
    print("6. 💡 Innovation Research (Quantum Computing)")
    print("7. 🌟 Custom Topic (Your Choice)")
    print("8. ❓ Help & Information")
    print("9. 🚪 Exit")
    print()


_CONFIGS: dict[str, dict] = {
    "1": {"name": "Technology Research", "topic": "OpenCV computer vision library — recent features and real-world applications"},
    "2": {"name": "Market Analysis", "topic": "Electric Vehicle market trends — growth, key players, adoption barriers"},
    "3": {"name": "Business Intelligence", "topic": "AI startup ecosystem — funding trends, market gaps, investment opportunities"},
    "4": {"name": "Content Strategy", "topic": "Social Media marketing for B2B SaaS — platforms, formats, ROI measurement"},
    "5": {"name": "Technical Analysis", "topic": "Cloud architecture best practices — microservices, security, cost optimisation"},
    "6": {"name": "Innovation Research", "topic": "Quantum computing applications — current limitations and near-term value"},
}


def run_custom_demo() -> dict | None:
    print("🌟 Custom Topic Analysis")
    print("=" * 30)
    topic = input("Enter your research topic: ").strip()
    if not topic:
        print("❌ No topic provided. Returning to menu...")
        return None
    return {"name": "Custom Analysis", "topic": topic}


def show_help() -> None:
    print(
        """
🔍 Strands Template Demo — Help

What happens during a demo:
  1. Researcher (Haiku 4.5) gathers sources via Serper + http_request.
  2. Analyst (Sonnet 4.6) converts findings into a Pydantic AnalysisReport.
  3. Editor (Opus 4.7) writes the final markdown report — saved to report.md.

Best practices:
  • Be specific with topics for better results.
  • Set SERPER_API_KEY for live web search; without it the researcher uses
    http_request only.

Docker commands:
  docker compose run --rm agent python demo.py
  docker compose run --rm agent python -m strands_template.main "Your topic"
  docker compose run --rm agent python examples/graph/research_graph.py
  docker compose run --rm agent python examples/swarm/research_swarm.py

Press Enter to return to the menu...
"""
    )
    input()


def run_demo(config: dict | None) -> None:
    if not config:
        return
    print(f"\n🚀 Starting {config['name']}...")
    print("=" * 50)
    print(f"📊 Topic: {config['topic']}")
    print(f"📅 Year:  {datetime.now().year}")
    print("⏱️  This may take a few minutes...\n")
    try:
        run_workflow(config["topic"])
        print("\n" + "=" * 60)
        print("✅ Done — see report.md for the full output.")
        print("=" * 60)
    except Exception as exc:  # noqa: BLE001 — demo wants to surface anything at all
        print(f"\n❌ Error during analysis: {exc}")
        print("💡 Make sure you have:")
        print("   • Provider creds set in .env (AWS Bedrock or ANTHROPIC_API_KEY)")
        print("   • Internet connection for tool calls")


def main() -> None:
    print_header()
    while True:
        show_menu()
        choice = input("Enter your choice (1-9): ").strip()
        if choice == "9":
            print("\n👋 Thanks for trying the Strands template!")
            break
        if choice == "8":
            show_help()
            continue
        if choice == "7":
            run_demo(run_custom_demo())
        elif choice in _CONFIGS:
            run_demo(_CONFIGS[choice])
        else:
            print("❌ Invalid choice. Please enter a number from 1-9.")
            continue
        input("\nPress Enter to continue...")
        print("\n" * 2)


if __name__ == "__main__":
    main()
