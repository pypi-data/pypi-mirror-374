from tinyurl_mcp.server import mcp


@mcp.prompt()
def mcp_user_prompt() -> str:
    """
    Prompt to help users interact and perform the supported operations.

    Returns:
        The prompt string
    """
    return """
    **Core Task:** Your responsibility is to help users perform the supported operations by using the available tools.

    **Supported Operations:**
    1. To generate a new short URL for a given long URL
    2. To modify the long URL of an existing short URL

    **Instructions:**
    1. Always start with understanding the user's request and plan the steps before executing the tools.
    2. Validate all the required inputs are provided by the user. If not, prompt for the required inputs.
    3. When a tool responds with an error code or message, strictly only suggest alternative approaches and never execute them with explicit user permission.
    """
