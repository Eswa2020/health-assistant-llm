# challenge29_invalid_tool.py
import asyncio
import os
import sys  # sys.executable = the exact Python interpreter running THIS script
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# CHANGED: absolute path to the server, based on where THIS file lives —
# avoids "file not found" if run from a different working directory.
# CHANGED: filename updated to match your actual server file
# (lab_20_MCP_server.py, which defines "get_market_trends").
SERVER_SCRIPT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "lab_20_MCP_server.py"
)

async def main():
    server_params = StdioServerParameters(
        # CHANGED: sys.executable guarantees the server subprocess uses
        # the SAME Python/venv as this client, avoiding the "Connection
        # closed" crash we hit earlier when "python" resolved incorrectly.
        command=sys.executable,
        args=[SERVER_SCRIPT]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            try:
                # WHY THIS IS INVALID: "invalid_tool_name" was never
                # registered on the server. Look back at lab_20_MCP_server.py
                # — its @server_app.list_tools() function only returns ONE
                # tool: "get_market_trends". There is no function anywhere
                # decorated or registered under the name "invalid_tool_name".
                # When the client asks the server to run a tool it doesn't
                # recognize, the server's @server_app.call_tool() handler
                # hits its own fallback:
                #     raise ValueError(f"Tool '{name}' not found.")
                # That error travels back across the connection to the
                # client as an MCP-level error, which is what gets caught
                # below.
                await session.call_tool("invalid_tool_name", arguments={})
            except Exception as e:
                # THE REAL LESSON: catching this here proves the SESSION
                # ITSELF survives a bad tool call. One failed request does
                # NOT kill the whole connection — this is different from
                # our earlier "Connection closed" bugs, where the entire
                # subprocess died. Here, only the single bad call fails;
                # everything else keeps working, as proven right below.
                print(f"Expected error caught: {e}")

            # Session remains alive; we can still call valid tools.
            # This line is the actual PROOF of the lesson above: if the
            # exception above had crashed the whole session, this call
            # would never even run. The fact that it succeeds confirms
            # the client recovered gracefully from the invalid tool call.
            result = await session.call_tool("get_market_trends", arguments={"region": "Kenya"})
            print("Valid tool result:", result)

asyncio.run(main())