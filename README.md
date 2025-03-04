# Eka MCP Server

## Overview
Eka MCP Server implements a Model Context Protocol server that provides note-taking functionality to compatible clients.

## Components

### Tools

The server implements one tool:
- **add-note**: Adds a new note to the server
  - Takes `name` and `content` as required string arguments
  - Updates server state and notifies clients of resource changes

## Configuration
Configuration is handled through command-line arguments when launching the server:
- `--eka-api-host`: The host URL for the Eka API
- `--client-id`: Your client ID for authentication
- `--client-token`: Your client token for authentication

## Quickstart
This MCP tool works with any STDIO-supported client. 
The instructions below are for installing on clients that support STDIO communication.

### Install on Claude

#### Claude Desktop

Configuration file locations:
- On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
- On Windows: `%APPDATA%/Claude/claude_desktop_config.json`


#### Development/Unpublished Servers Configuration
```json
{
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
}
```

#### Published Servers Configuration
  
```json
{
  "mcpServers": {
    "eka-assist": {
      "command": "uvx",
      "args": [
        "eka-assist"
      ]
    }
  }
}
```


### Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging
experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).

You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
npx @modelcontextprotocol/inspector uv --directory <eka_mcp_server_folder_path> run eka_assist
```

Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.

## Usage
Once installed, the Eka MCP server will be available to your Claude client. You can use the `add-note` tool to create and store notes through the Claude interface.

## Support
For additional support, please refer to the documentation or contact the Eka support team.