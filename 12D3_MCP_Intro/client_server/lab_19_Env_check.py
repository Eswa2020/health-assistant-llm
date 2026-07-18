# challenge24_env_check.py
import os
import sys  # sys.executable = the exact Python interpreter running THIS script
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv  # ADDED: needed to actually read the .env file

# ADDED: without this call, os.getenv() below will never see anything
# from your .env file — it only reads variables already loaded into the
# real OS environment. Same "load before you check" rule from before.
load_dotenv()

REQUIRED_ENV = ["OPENAI_API_KEY", "AFYAPLUS_REGION"]  # example flags

def check_environment():
    """
    Confirms every required environment variable is actually present
    before doing any real work. 'Fail fast, fail clearly': better to stop
    immediately with a clear message than crash confusingly later.
    """
    missing = [var for var in REQUIRED_ENV if not os.getenv(var)]
    if missing:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")

async def main():
    check_environment()

    # CHANGED: build an ABSOLUTE path to the server script, based on where
    # THIS file lives — not on whatever folder you happen to be in when
    # you run the command. Prevents "file not found" if run from elsewhere.
    # CHANGED: filename updated to match your actual server file.
    server_script = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "lab_20_MCP_server.py"
    )

    server_params = StdioServerParameters(
        # CHANGED: sys.executable guarantees the server subprocess runs
        # with the SAME Python/venv as this client. Using the plain string
        # "python" risks picking a different interpreter that may be
        # missing the `mcp` package, causing an instant crash that shows
        # up here as "Connection closed".
        command=sys.executable,
        args=[server_script]  # CHANGED: now an absolute path, not relative
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("Connection successful. Tools found:", [t.name for t in tools.tools])

if __name__ == "__main__":
    asyncio.run(main())