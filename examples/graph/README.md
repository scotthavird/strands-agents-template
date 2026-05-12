# Graph example

Same three agents, wired with `GraphBuilder` as a deterministic directed
graph. Output from each node feeds the next; conditional edges only
traverse when their predicate returns True.

Use this pattern when you want:

- Explicit dependencies between agents
- Conditional routing (e.g. skip the editor on weak analyses)
- A nested multi-agent structure (a node can itself be a Swarm or sub-Graph)

Run:

```bash
docker compose run --rm agent python examples/graph/research_graph.py
```
