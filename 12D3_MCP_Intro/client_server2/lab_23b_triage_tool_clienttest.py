# challenge28_client_test.py
import asyncio
import os
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_SCRIPT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "lab_23_triage_tool.py"
)

async def main():
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[SERVER_SCRIPT]
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Confirm the tool is discoverable
            tools = await session.list_tools()
            print("Discovered tools:", [t.name for t in tools.tools])

            # Actually CALL the tool with a test symptom
            result = await session.call_tool("triage_lookup", {"symptom": "headaches and nausea"})
            print("Triage result:", result.content[0].text)

asyncio.run(main())