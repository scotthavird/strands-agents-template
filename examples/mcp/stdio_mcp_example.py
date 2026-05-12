#!/usr/bin/env python
"""MCP integration via stdio.

Connects to the AWS Documentation MCP server over stdio (`uvx`), pulls in
its tools, and asks an AWS question. This is the simplest MCP transport —
see https://strandsagents.com/docs/user-guide/concepts/tools/mcp-tools/
for SSE and streamable-HTTP variants.

Run inside the container:

    docker compose run --rm agent python examples/mcp/stdio_mcp_example.py
"""
from __future__ import annotations

from mcp import StdioServerParameters, stdio_client
from strands import Agent
from strands.tools.mcp import MCPClient

from strands_template.agents import _build_model  # type: ignore[attr-defined]
from strands_template.observability import ConsoleHookProvider


def main() -> None:
    aws_docs_client = MCPClient(
        lambda: stdio_client(
            StdioServerParameters(
                command="uvx",
                args=["awslabs.aws-documentation-mcp-server@latest"],
            )
        )
    )

    with aws_docs_client:
        tools = aws_docs_client.list_tools_sync()
        print(f"loaded {len(tools)} tools from AWS Documentation MCP server")

        agent = Agent(
            model=_build_model("researcher"),
            system_prompt=(
                "You are an AWS specialist. Use the AWS Documentation MCP "
                "tools to answer questions accurately and cite the doc URL."
            ),
            tools=tools,
            hooks=[ConsoleHookProvider()],
        )
        response = agent(
            "What are the cold-start optimisation options for AWS Lambda? "
            "Cite the relevant doc URLs."
        )
        print("\n— agent response —")
        print(response)


if __name__ == "__main__":
    main()
