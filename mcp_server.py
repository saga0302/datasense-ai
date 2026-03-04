from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
import json

server = Server("datasense-pipeline-tools")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="scan_pipelines",
            description="Scan all data pipelines and return failed ones",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
        types.Tool(
            name="get_downstream_impact",
            description="Get downstream systems affected by a failed pipeline",
            inputSchema={
                "type": "object",
                "properties": {
                    "pipeline_name": {"type": "string", "description": "Name of the failed pipeline"}
                },
                "required": ["pipeline_name"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "scan_pipelines":
        from data.mock_data import MOCK_PIPELINES
        failed = [p for p in MOCK_PIPELINES if p["status"] == "FAILED"]
        return [types.TextContent(type="text", text=json.dumps(failed, indent=2))]

    elif name == "get_downstream_impact":
        from data.mock_data import DEPENDENCY_MAP
        pipeline_name = arguments.get("pipeline_name", "")
        deps = DEPENDENCY_MAP.get(pipeline_name, {})
        return [types.TextContent(type="text", text=json.dumps(deps, indent=2))]

async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream,
            InitializationOptions(
                server_name="datasense-pipeline-tools",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())