# lab_18_MCP_client.py
import asyncio
import os
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lab_20_MCP_server.py")

server_params = StdioServerParameters(
    command=sys.executable,   # guarantees the SAME python/venv that's running this client
    args=[SERVER_SCRIPT]
)

async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("Discovered tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")

asyncio.run(main())