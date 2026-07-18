# challenge28_mcp_triage_tool.py
from mcp.server.fastmcp import FastMCP

# FastMCP is a higher-level, simpler way to build an MCP server compared
# to the low-level Server class + @server_app.list_tools() /
# @server_app.call_tool() pattern from lab_20_MCP_server.py. FastMCP
# handles a lot of the boilerplate (tool registration, schema generation)
# automatically, based on your function's type hints and docstring.
server = FastMCP("afyaplus-clinic")

@server.tool()
def triage_lookup(symptom: str) -> str:
    """Determine the urgency level of a patient symptom.
    Use this tool when a user reports a symptom and asks how urgent it is."""
    # The docstring above isn't just documentation for humans — FastMCP
    # automatically turns it into the tool's "description" field, exactly
    # like the description= you had to write manually in lab_20's Tool(...)
    # definition. Same for the symptom: str type hint — FastMCP auto-builds
    # the JSON inputSchema from it, instead of you writing it by hand.

    symptom_lower = symptom.lower()
    if any(word in symptom_lower for word in ["chest pain", "bleeding", "unconscious"]):
        return "EMERGENCY \u2013 seek immediate medical attention."
    elif any(word in symptom_lower for word in ["headache", "fever", "cough"]):
        return "MODERATE \u2013 schedule an appointment within 24 hours."
    else:
        return "LOW \u2013 self-care advised. Contact clinic if symptoms worsen."

if __name__ == "__main__":
    server.run()  # FastMCP starts the server automatically, listening on stdio