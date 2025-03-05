# Eka MCP Server

## Overview

Healthcare professionals frequently need to switch context to access additional information while treating patients. While AI can serve as a bridge to provide this information, there is an inherent risk of hallucination. The Eka MCP server addresses this challenge by grounding Large Language Model (LLM) responses in curated medical information from eka.care.

The Model Context Protocol (MCP) functions as a universal interface for AI applications, enabling LLMs to access and utilize relevant information effectively. While there are many open-source MCP servers available, the Eka MCP server specifically targets healthcare use cases with curated medical tools.

## Features

### Curated Tools

1. **Medications**
   - **Medication Understanding**: Access to a comprehensive corpus of drugs for various treatments. The LLM can intelligently recommend appropriate brands for specific diseases.
   - **Medication Interaction**: Check for interactions between drugs and identify medications with identical generic compositions.

2. **Protocols**
   - Standardized guidelines, procedures, and decision pathways for healthcare professionals to follow when diagnosing and treating specific conditions.
   - Serve as comprehensive roadmaps for clinical care, ensuring consistent and evidence-based treatment approaches.
   - **Publishers**: Organizations responsible for developing, validating, distributing, and maintaining medical protocols.
   - **Tags and Conditions**: Metadata related to diseases, disorders, or clinical situations that protocols address.

## How It Works

Medical protocol adherence is critical, as even slight deviations can lead to serious consequences. The Eka MCP server follows specific steps to ensure accurate responses:

1. Users can request treatment protocols for diseases without providing basic knowledge.
2. Tags and conditions must be verified since treatments vary accordingly.
3. Once the user verifies the condition, a list of relevant publications is presented.
4. After the user confirms a publication, treatment protocols are provided in the response.

## Installation and Setup for Claude

1. Download and install Claude desktop application.
2. Locate the configuration file:
   - **macOS**: `/Library/Application\ Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

3. Modify the configuration file with the following settings:

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

4. Replace the placeholder values:
   - `<eka_mcp_server_folder_path>`: Path to the folder containing the Eka MCP server
   - `<eka_api_host>`: Eka API host URL
   - `<client_id>`: Your client ID
   - `<client_token>`: Your client token

> **Note**: You can obtain the `eka-api-host`, `client-id`, and `client-token` from developer tools or by contacting the Eka support team.

## Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging experience, we recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).

You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
npx @modelcontextprotocol/inspector uv --directory <eka_mcp_server_folder_path> run eka_assist
```

Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.

## Usage

Once installed and configured correctly, the Eka MCP server will be available to your Claude client. You can interact with the available tools through the Claude interface to:

- Look up medications and their compositions
- Check for drug interactions
- Access treatment protocols for specific conditions
- Verify treatment guidelines from trusted medical publications

## Support

For additional support, please refer to the complete documentation or contact the Eka support team at support@eka.care.