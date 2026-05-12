# Examples

Same three agents (researcher → analyst → editor), three different
orchestration topologies, plus an MCP example. Pick the shape that fits
your workload.

| Example | Pattern | When to use |
|---|---|---|
| [`business_analysis_example.py`](business_analysis_example.py) | Sequential workflow with a baked-in topic | One-shot prototypes, scripted runs |
| [`graph/research_graph.py`](graph/research_graph.py) | `GraphBuilder` deterministic DAG | You want explicit dependencies and conditional edges |
| [`swarm/research_swarm.py`](swarm/research_swarm.py) | `Swarm` with handoffs | Agents should self-organise; topology is emergent |
| [`mcp/stdio_mcp_example.py`](mcp/stdio_mcp_example.py) | Pull tools from an MCP server | You want third-party tools without writing wrappers |

All examples run inside the container:

```bash
docker compose run --rm agent python examples/business_analysis_example.py
docker compose run --rm agent python examples/graph/research_graph.py
docker compose run --rm agent python examples/swarm/research_swarm.py
docker compose run --rm agent python examples/mcp/stdio_mcp_example.py
```
