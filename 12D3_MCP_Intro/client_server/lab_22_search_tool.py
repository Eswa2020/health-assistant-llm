# challenge27_search_tool.py
import asyncio
import os
import sys  # sys.executable = the exact Python interpreter running THIS script
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# CHANGED: absolute path to the server script, based on where THIS file
# lives — avoids "file not found" if run from a different working
# directory. Filename updated to match your actual server file.
SERVER_SCRIPT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "lab_20_MCP_server.py"
)

async def main():
    server_params = StdioServerParameters(
        # CHANGED: sys.executable guarantees the server subprocess uses
        # the SAME Python/venv as this client, avoiding the "Connection
        # closed" crash from earlier when "python" resolved incorrectly.
        command=sys.executable,
        args=[SERVER_SCRIPT]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()

            # Search for a specific tool by name.
            # any(...) checks each tool in the list and returns True the
            # moment ONE of them matches target_name — it stops checking
            # as soon as it finds a match, rather than scanning everything.
            target_name = "get_market_trends"
            found = any(tool.name == target_name for tool in tools.tools)

            if found:
                print(f"Tool '{target_name}' is available.")
            else:
                print(f"Tool '{target_name}' not found.")

asyncio.run(main())