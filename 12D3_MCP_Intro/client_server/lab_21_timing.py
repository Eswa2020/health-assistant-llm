# challenge26_timing.py
import asyncio
import os
import sys  # sys.executable = the exact Python interpreter running THIS script
import time
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# CHANGED: build an ABSOLUTE path to the server script, based on where THIS
# file lives — not on whatever folder you happen to be in when you run the
# command. Prevents "file not found" if run from elsewhere.
# CHANGED: filename updated to match your actual server file.
SERVER_SCRIPT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "lab_20_MCP_server.py"
)

async def main():
    server_params = StdioServerParameters(
        # CHANGED: sys.executable guarantees the server subprocess runs
        # with the SAME Python/venv as this client, avoiding the
        # "Connection closed" crash we hit when "python" resolved to the
        # wrong interpreter (one missing the mcp package).
        command=sys.executable,
        args=[SERVER_SCRIPT]
    )

    # time.time() records the current moment as a number (seconds).
    # Capturing it before and after lets us measure exactly how long the
    # whole connect + discover-tools cycle took — same timing pattern
    # from our Week 1 cloud-vs-local latency comparison lab.
    start = time.time()

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("Discovered tools:", [t.name for t in tools.tools])

    elapsed = time.time() - start
    print(f"Session took {elapsed:.2f} seconds")

asyncio.run(main())