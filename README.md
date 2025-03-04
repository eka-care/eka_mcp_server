# Eka MCP server


## Components

### Tools

The server implements one tool:
- add-note: Adds a new note to the server
  - Takes "name" and "content" as required string arguments
  - Updates server state and notifies clients of resource changes

## Configuration


## Quickstart
This MCP tool will work with any STDIO supported client. 
The instructions below are for installing on clients that support STDIO communication.

### Install on Claude

#### Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Servers Configuration</summary>

    "mcpServers": {
      "eka-assist": {
        "command": "uv",
        "args": [
          "--directory",
          "<eka_mcp_server_folder_path>",
          "run",
          "eka_assist",
          "--eka-api-host",
          "<eka_api_host>",
          "--client-id",
          "<client_id>",
          "--client-token",
          "<client_token>"
        ]
      }
    }
</details>

<details>
  <summary>Published Servers Configuration</summary>
  
    "mcpServers": {
      "eka-assist": {
        "command": "uvx",
        "args": [
          "eka-assist"
        ]
      }
    }
  
</details>

### Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging
experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).


You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```
npx @modelcontextprotocol/inspector uv --directory <eka_mcp_server_folder_path> run eka_assist
```


Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.