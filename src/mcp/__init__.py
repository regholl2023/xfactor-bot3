"""
MCP (Model Context Protocol) Server for XFactor Bot.
Allows AI assistants to interact with the trading system.
"""

from src.mcp.server import MCPServer, get_mcp_server

__all__ = ["MCPServer", "get_mcp_server"]

