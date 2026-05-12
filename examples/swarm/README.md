# Swarm example

Same three agents, but coordinated as a `Swarm` — emergent handoffs,
shared working memory, no fixed topology. The researcher is the entry
point; agents pass control to each other via Strands' built-in handoff
tools when they decide their part is done.

Use this pattern when:

- You don't know the right execution order in advance
- Agents need to inspect each other's progress and react
- The problem genuinely benefits from collective intelligence

Run:

```bash
docker compose run --rm agent python examples/swarm/research_swarm.py
```
