import asyncio
import json

def scan_pipelines_via_mcp() -> str:
    """Scan pipelines — tries MCP first, falls back to mock data"""
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        async def _call():
            server_params = StdioServerParameters(
                command="python",
                args=["mcp_server.py"]
            )
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool("scan_pipelines", {})
                    return result.content[0].text

        return asyncio.run(_call())

    except Exception:
        # Fallback for Streamlit Cloud — read directly from mock data
        from data.mock_data import MOCK_PIPELINES
        failed = [p for p in MOCK_PIPELINES if p["status"] == "FAILED"]
        return json.dumps(failed, indent=2)


def get_downstream_via_mcp(pipeline_name: str) -> str:
    """Get downstream impact — tries MCP first, falls back to mock data"""
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        async def _call():
            server_params = StdioServerParameters(
                command="python",
                args=["mcp_server.py"]
            )
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(
                        "get_downstream_impact",
                        {"pipeline_name": pipeline_name}
                    )
                    return result.content[0].text

        return asyncio.run(_call())

    except Exception:
        # Fallback for Streamlit Cloud — read directly from mock data
        from data.mock_data import DEPENDENCY_MAP
        deps = DEPENDENCY_MAP.get(pipeline_name, {
            "upstream_sources": [],
            "downstream_dependents": [],
            "shared_infrastructure": []
        })
        return json.dumps(deps, indent=2)