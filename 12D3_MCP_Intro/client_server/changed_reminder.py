# lab_18_MCP_client.py
import asyncio
import os
import sys  # sys.executable = the exact Python interpreter currently running this script
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Build an ABSOLUTE path to the server script, based on where THIS file lives,
# not on whatever folder you happen to be sitting in when you run the command.
# This avoids "file not found" style crashes if you run python from a
# different directory than expected.
SERVER_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lab_20_MCP_server.py")

server_params = StdioServerParameters(
    # sys.executable guarantees the SAME Python/venv that is running THIS
    # client script also runs the server subprocess. Using the plain string
    # "python" is risky: on a machine with multiple Python installs/venvs
    # (like ours, after all the venv mixups this session), "python" might
    # resolve to a DIFFERENT interpreter that doesn't have the `mcp` package
    # installed — causing the server subprocess to crash instantly on
    # import, which looks like "Connection closed" from the client's side.
    command=sys.executable,
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