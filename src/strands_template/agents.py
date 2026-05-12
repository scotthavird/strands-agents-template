"""Build the three right-sized agents.

Each agent's model is selected by `_build_model()` — Anthropic API if
`ANTHROPIC_API_KEY` is set, otherwise Bedrock (Strands' native default,
auto-picks up `AWS_*` / `AWS_BEARER_TOKEN_BEDROCK` from env).

Per-agent overrides win over the env-default `MODEL`. Knowledge files in
`knowledge/` are appended to every agent's system prompt — the Strands
substitute for crewAI's `TextFileKnowledgeSource`.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import yaml
from strands import Agent
from strands_tools import http_request

from strands_template.tools import DataAnalyzer, serper_search, word_count

_DEFAULT_MODELS_BEDROCK = {
    "researcher": "anthropic.claude-haiku-4-5-20251001-v1:0",
    "analyst": "anthropic.claude-sonnet-4-6-20250514-v1:0",
    "editor": "anthropic.claude-opus-4-7-20251001-v1:0",
}

_DEFAULT_MODELS_ANTHROPIC = {
    "researcher": "claude-haiku-4-5",
    "analyst": "claude-sonnet-4-6",
    "editor": "claude-opus-4-7",
}


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_yaml(rel_path: str) -> dict:
    return yaml.safe_load((Path(__file__).parent / rel_path).read_text())


def _load_knowledge() -> str:
    knowledge_dir = _project_root() / "knowledge"
    if not knowledge_dir.is_dir():
        return ""
    snippets: list[str] = []
    for path in sorted(knowledge_dir.glob("*.txt")):
        snippets.append(f"--- {path.name} ---\n{path.read_text().strip()}")
    if not snippets:
        return ""
    return "\n\nBackground knowledge (treat as authoritative for your client):\n\n" + "\n\n".join(snippets)


def _is_anthropic_path() -> bool:
    return bool(os.getenv("ANTHROPIC_API_KEY"))


def _resolve_model_id(role: str) -> str:
    override = os.getenv(f"{role.upper()}_MODEL", "").strip()
    if override:
        return override
    env_default = os.getenv("MODEL", "").strip()
    if env_default:
        return env_default
    table = _DEFAULT_MODELS_ANTHROPIC if _is_anthropic_path() else _DEFAULT_MODELS_BEDROCK
    return table[role]


_MAX_TOKENS = {"researcher": 2048, "analyst": 4096, "editor": 8192}


def _build_model(role: str):
    model_id = _resolve_model_id(role)
    temperature = 0.4 if role == "researcher" else 0.3
    if _is_anthropic_path():
        from strands.models.anthropic import AnthropicModel

        return AnthropicModel(
            model_id=model_id,
            client_args={"api_key": os.getenv("ANTHROPIC_API_KEY")},
            max_tokens=_MAX_TOKENS[role],  # type: ignore[arg-type]  # int per upstream docs; some stub revisions type as str
            params={"temperature": temperature},
        )
    from strands.models import BedrockModel

    return BedrockModel(model_id=model_id, temperature=temperature)


def _build_agent(role: str, configs: dict, knowledge: str, tools: list, hooks: Optional[list] = None) -> Agent:
    spec = configs[role]
    system_prompt = (spec.get("system_prompt") or "").rstrip() + knowledge
    return Agent(
        name=spec.get("name", role),
        model=_build_model(role),
        system_prompt=system_prompt,
        tools=tools,
        hooks=hooks or [],
    )


def build_agents(hooks: Optional[list] = None) -> tuple[Agent, Agent, Agent]:
    """Build (researcher, analyst, editor) with right-sized models and tools.

    `hooks` is an optional list of `HookProvider` instances applied to all
    three agents — e.g. the ConsoleHookProvider from `observability.py`.
    """
    configs = _load_yaml("config/agents.yaml")
    knowledge = _load_knowledge()
    analyzer = DataAnalyzer()

    researcher = _build_agent(
        "researcher",
        configs,
        knowledge,
        tools=[serper_search, http_request, word_count],
        hooks=hooks,
    )
    analyst = _build_agent(
        "analyst",
        configs,
        knowledge,
        tools=[analyzer.sentiment_score, analyzer.top_terms, analyzer.key_phrases],
        hooks=hooks,
    )
    editor = _build_agent(
        "editor",
        configs,
        knowledge,
        tools=[],
        hooks=hooks,
    )
    return researcher, analyst, editor
