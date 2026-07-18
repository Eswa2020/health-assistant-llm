# lab_20_MCP_server.py for afyaplus 
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server_app = Server("afyaplus-mock-clinic-server")

@server_app.list_tools()
async def list_tools():
    """Return tools this server provides."""
    return [
        Tool(
            name="get_market_trends",
            description="Retrieves clinic performance metrics for East Africa.",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {"type": "string", "description": "Country name (e.g., 'Kenya')"}
                },
                "required": ["region"]
            }
        )
    ]

@server_app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "get_market_trends":
        region = arguments.get("region", "Unknown")
        return [TextContent(type="text", text=f"Verified Record for [{region}]: Nairobi claims velocity is up 14%.")]
    raise ValueError(f"Tool '{name}' not found.")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server_app.run(read_stream, write_stream, server_app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())

    