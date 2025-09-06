## TinyURL MCP Server

This MCP server provides tools to interact with [tinyurl.com](https://tinyurl.com) to manage short URLs.

### Prerequisites

- For Option 1:
  - [uv](https://docs.astral.sh/uv/) from Astral
  - [Python 3.13](https://www.python.org/downloads/) or higher
- For Option 2:
  - [Docker](https://www.docker.com/)


### Configuration

Use either of the below option to configure your MCP client. To understand the configuration options, please refer to the [documentation](https://gofastmcp.com/integrations/mcp-json-configuration).

**Option 1: Via uvx**
```json
{
  "mcpServers": {
    "tinyurl-mcp": {
      "command": "uvx",
      "args": [
        "tinyurl-mcp"
      ],
      "env": {
        "TINY_URL_API_KEY": "__API_KEY__"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```


**Option 2: Via docker**

```json
{
  "mcpServers": {
    "tinyurl-mcp": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--env",
        "TINY_URL_API_KEY=__API_KEY__",
        "vimalpaliwal/tinyurl-mcp:latest"
      ],
      "env": {},
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

**Note:** Replace `__API_KEY__` with your actual API key.


### Available Tools

- `generate_short_url`: Generate a new short URL
- `update_long_url`:  Update the long URL of an existing short URL
- `delete_short_url`: Delete an existing short URL
- `list_short_urls`: Llist all the available or archived short URLs

### Basic Usage Examples

- Shorten linkedin.com/in/xxxxx for me please
- Please create a short URL for medium.com/blog/xxxxx that expires next week
- Update the long URL of tinyurl.com/xxxx to medium.com/blog/zzzzz
- Delete the short URL for tinyurl.com/xxxx for me please
- List all the archived short URLs
