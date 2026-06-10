"""Production ASGI entry point for the rocket-tools MCP server."""

from rocket_tools.server import mcp

app = mcp.sse_app()
