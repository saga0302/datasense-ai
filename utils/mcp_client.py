import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def call_mcp_tool(tool_name: str, arguments: dict = {}) -> str:
    """Call a tool on the MCP server and return the result"""
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            return result.content[0].text

def scan_pipelines_via_mcp() -> str:
    """Synchronous wrapper — scan all pipelines through MCP"""
    return asyncio.run(call_mcp_tool("scan_pipelines"))

def get_downstream_via_mcp(pipeline_name: str) -> str:
    """Synchronous wrapper — get downstream impact through MCP"""
    return asyncio.run(call_mcp_tool(
        "get_downstream_impact",
        {"pipeline_name": pipeline_name}
    ))