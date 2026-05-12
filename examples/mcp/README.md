# MCP example

Connects to the AWS Documentation MCP server over stdio (`uvx`),
loads its tools into a fresh agent, and asks an AWS question. This is
the canonical Strands MCP integration — three transports are supported
(stdio, SSE, streamable-HTTP) but stdio is the easiest to demo.

Run:

```bash
docker compose run --rm agent python examples/mcp/stdio_mcp_example.py
```

Notes:

- Requires `uvx` (ships with `uv`); installed in the container.
- The `with mcp_client:` context-managed form is the explicit-lifecycle
  variant. The `Agent(tools=[mcp_client])` form auto-manages it.
- Add tool filters via `MCPClient(..., tool_filters={"allowed": [...]})`
  to narrow the tool surface, or `prefix=` to namespace tools when you
  combine multiple servers.
