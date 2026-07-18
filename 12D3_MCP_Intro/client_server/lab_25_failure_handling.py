# challenge25_failure_handling.py
import asyncio
import sys  # ADDED: sys.executable = the exact Python interpreter running THIS script
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        # CHANGED: sys.executable guarantees whatever Python/venv is running
        # this client is also the one attempting to launch the server —
        # removes any ambiguity about which "python" gets picked, same fix
        # as our earlier labs.
        command=sys.executable,
        # NOTE: "non_existent_server.py" is INTENTIONAL here — this is the
        # whole point of the exercise. We're deliberately pointing at a file
        # that doesn't exist, to prove our error handling actually catches
        # the failure gracefully instead of crashing with a raw traceback.
        args=["non_existent_server.py"]
    )
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                print("Tools:", tools)
    except Exception as e:
        # This is the actual lesson: catching the failure here means the
        # program prints a clean, readable message and exits normally,
        # rather than dumping a scary multi-line traceback like we saw
        # with our earlier real "Connection closed" bugs. This is the
        # SAME underlying error type (connection/subprocess failure) —
        # the difference is this script is designed to handle it on
        # purpose, not accidentally trigger it like before.
        print(f"Could not start server: {e}")

asyncio.run(main())