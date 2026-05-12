# Strands Agents Template

An opinionated, modern starter for **[Strands Agents](https://strandsagents.com)**.
Clone, set provider credentials, run one command — and you get every canonical
pattern an engineer needs to ship a real multi-agent app.

## What you get

A 3-agent **research → analysis → report** pipeline expressed three ways
(sequential workflow, deterministic graph, emergent swarm), three custom
tools, an MCP integration, and the production scaffolding you'd otherwise
spend a week stitching from the docs:

|  | Pattern | Where |
|---|---|---|
| 🧩 | YAML-driven `agents.yaml` / `tasks.yaml` config + Python builder | `src/strands_template/{config,agents.py}` |
| 🛣️ | **Sequential workflow** with structured output + guardrail | `src/strands_template/workflow.py` |
| 🕸️ | **`GraphBuilder`** deterministic DAG with conditional edges | `examples/graph/research_graph.py` |
| 🐝 | **`Swarm`** with handoffs, shared memory, entry-point routing | `examples/swarm/research_swarm.py` |
| 🔌 | **MCP** integration via stdio (`uvx`) — pulls AWS docs tools | `examples/mcp/stdio_mcp_example.py` |
| 🛠️ | `@tool` decorator (function-style) + class-style with `@tool` methods | `src/strands_template/tools/` |
| 🔎 | Serper.dev web search + `http_request` (graceful no-key fallback) | `tools/serper_search.py` + `agents.py` |
| 📚 | Plain-text knowledge files injected into every agent's system prompt | `knowledge/company_brief.txt` |
| 🧠 | `SlidingWindowConversationManager` + `FileSessionManager` REPL | `main.py:chat` |
| 🎯 | **Per-agent model right-sizing** — Haiku 4.5 / Sonnet 4.6 / Opus 4.7 | `agents.py:_build_model` |
| 🧱 | `agent.structured_output(AnalysisReport, …)` Pydantic schema | `workflow.py` + `schemas.py` |
| 🛡️ | Markdown-shape guardrail with up-to-2 retries | `schemas.py:ensure_markdown_report` |
| 🔁 | Provider auto-switch — Bedrock-first, Anthropic API alternative | `agents.py:_build_model` |
| 📡 | Console `HookProvider` printing tool start/complete | `observability.py:ConsoleHookProvider` |
| 📈 | Optional OTLP export via `StrandsTelemetry()` | `observability.py:enable_otel` |
| ✅ | `pytest` suite (tools, guardrails, gated smoke test) | `tests/` |

Everything runs inside Docker so the experience is identical on any machine.

## Quick start

```bash
git clone https://github.com/scotthavird/strands-agents-template
cd strands-agents-template
cp .env.example .env
# edit .env — set EITHER:
#   AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY (or AWS_BEARER_TOKEN_BEDROCK)
#   …OR ANTHROPIC_API_KEY
docker compose build
docker compose run --rm agent python -m strands_template.main
```

The first run researches `"OpenCV"` by default. Pass a topic:

```bash
docker compose run --rm agent python -m strands_template.main "Edge AI in 2026"
```

When it finishes you'll have a `report.md` written by the editor agent
and (if you set `SERPER_API_KEY`) genuine web-sourced findings.

## The pipeline

```
   research_task            analysis_task                report_task
  ┌────────────┐  context   ┌────────────┐   context    ┌────────────┐
  │ researcher │ ─────────▶ │  analyst   │ ───────────▶ │   editor   │
  └────────────┘            └────────────┘              └────────────┘
   Claude Haiku 4.5          Claude Sonnet 4.6           Claude Opus 4.7
   serper_search             DataAnalyzer methods        (no tools — writes)
   http_request              structured_output(...)      guardrail + retries
   word_count                AnalysisReport (Pydantic)   1M context
```

Each agent's model is **right-sized to its workload**:

- **researcher** — Haiku 4.5 (cheap, fast, tool-call-heavy). Many small
  tool calls dominate latency, so a lightweight model wins.
- **analyst** — Sonnet 4.6 best-in-class for `agent.structured_output(AnalysisReport, …)`.
- **editor** — Opus 4.7 (1M context handles the full upstream research dump
  without truncation), guardrail with up-to-2 retries on too-short or
  unstructured output.

The default `MODEL` env var is the fallback used by any agent without a
per-agent override (`RESEARCHER_MODEL` / `ANALYST_MODEL` / `EDITOR_MODEL`).
Setting all three to a single model is fine if you want a uniform run.

### Provider selection

The template auto-switches based on which credentials are set:

| You set | You get |
|---|---|
| `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` (or `AWS_BEARER_TOKEN_BEDROCK`) | `BedrockModel` (Strands' native default) |
| `ANTHROPIC_API_KEY` | `AnthropicModel` (lower-friction alternative) |

Both paths run identical code. Bedrock is the documented primary because
Strands is an AWS project; Anthropic API is the path of least resistance
on a bare laptop.

## The three orchestration variants

Strands' selling point versus a single `Agent` is **first-class multi-agent
orchestration**. The same three agents are wired three different ways so
you can pick the shape that fits your problem:

| Topology | When to use | File |
|---|---|---|
| **Sequential** (`workflow.py`) | One-shot pipelines with known order. Easiest to debug. | `src/strands_template/workflow.py` |
| **Graph** (`GraphBuilder`) | Explicit dependencies, conditional edges, nested multi-agent groups. | `examples/graph/research_graph.py` |
| **Swarm** (`Swarm`) | Emergent coordination via handoffs and shared memory; topology decided at runtime. | `examples/swarm/research_swarm.py` |

```bash
# Sequential (default)
docker compose run --rm agent python -m strands_template.main "<topic>"

# Graph
docker compose run --rm agent python examples/graph/research_graph.py "<topic>"

# Swarm
docker compose run --rm agent python examples/swarm/research_swarm.py "<topic>"
```

## MCP

Strands has first-class **Model Context Protocol** support — three transports
(stdio / SSE / streamable-HTTP), automatic lifecycle management, tool
filtering, and prefix-based namespacing for multi-server setups.

```bash
docker compose run --rm agent python examples/mcp/stdio_mcp_example.py
```

The shipped example connects to `awslabs.aws-documentation-mcp-server`
over stdio and asks an AWS question. Swap in any MCP server (GitHub,
Postgres, Slack, …) by changing the `StdioServerParameters` block — see
[the docs](https://strandsagents.com/docs/user-guide/concepts/tools/mcp-tools/).

## Interactive REPL with sessions

```bash
docker compose run --rm agent strands-chat my-session-id
```

Wraps the editor agent with `SlidingWindowConversationManager` (window
size 20) and `FileSessionManager` (saved under `.sessions/<id>/`). Quit
with Ctrl-D; resume by passing the same id later.

## Tests

```bash
docker compose run --rm agent pytest                    # tool + guardrail unit tests
RUN_INTEGRATION=1 docker compose run --rm agent pytest  # also hit a real LLM
```

## Customising

Forking this for a new project? Run:

```bash
./setup.sh my_project_name
```

It renames the package, updates imports, and prompts for author / description.
Then customise:

- **Agents & roles** — `src/strands_template/config/agents.yaml`
- **Tasks / prompts** — `src/strands_template/config/tasks.yaml`
- **Tools** — drop new `@tool` functions in `src/strands_template/tools/` and re-export in `__init__.py`
- **Knowledge** — drop `*.txt` files in `knowledge/` (auto-injected into every agent's system prompt)
- **Topology** — edit `workflow.py`, or fork an example under `examples/`

## Production add-ons

These are commented out in the template — flip them on when you need them:

- **OpenTelemetry** — uncomment `OTEL_*` in `.env`; `enable_otel()` in
  `observability.py` calls `StrandsTelemetry().setup_otlp_exporter()` for you
- **Per-agent model overrides** — `RESEARCHER_MODEL` / `ANALYST_MODEL` /
  `EDITOR_MODEL` in `.env`, override the right-sized defaults
- **Bedrock guardrails** — pass `guardrail_id=` and `guardrail_version=` to
  `BedrockModel(...)` in `agents.py:_build_model`
- **Hooks beyond logging** — implement `HookProvider` for retry-on-bad-output,
  PII redaction, cost capping, etc.; see Strands' hook events: `BeforeInvocationEvent`,
  `AfterInvocationEvent`, `BeforeToolCallEvent`, `AfterToolCallEvent`, `MessageAddedEvent`
- **Async streaming** — `agent.stream_async(prompt)` in any handler that
  needs token-by-token output; see the `process_streaming_response` recipe
  in the [Strands quickstart](https://strandsagents.com/docs/user-guide/quickstart/python/)
- **A2A protocol** — wrap a remote agent as a tool with `A2AAgent` for
  cross-process collaboration

## Learning path

1. **Run it.** `docker compose run --rm agent python -m strands_template.main` and watch the console output — the `ConsoleHookProvider` prints every tool call.
2. **Open `agents.py`.** All three agents and the provider auto-switch are one screen of code.
3. **Open `workflow.py`.** Sequential pipeline with `structured_output` and the markdown guardrail.
4. **Compare `examples/graph/` and `examples/swarm/`.** Same agents, different topologies.
5. **Pin docs:** [Quickstart](https://strandsagents.com/docs/user-guide/quickstart/python/) · [Tools](https://strandsagents.com/docs/user-guide/concepts/tools/python-tools/) · [MCP](https://strandsagents.com/docs/user-guide/concepts/tools/mcp-tools/) · [Multi-agent](https://strandsagents.com/docs/user-guide/concepts/multi-agent/) · [Hooks](https://strandsagents.com/docs/user-guide/concepts/agents/hooks/) · [Observability](https://strandsagents.com/docs/user-guide/observability-evaluation/observability/)

---

**License:** MIT (see `LICENSE`).
