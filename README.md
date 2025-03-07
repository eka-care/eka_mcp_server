# Eka MCP Server

## Overview

Healthcare professionals frequently need to switch context to access additional information while treating patients. While AI can serve as a bridge to provide this information, there is an inherent risk of hallucination. 
The Eka MCP Server addresses this challenge by:

* Grounding LLM responses in curated medical information from eka.care
* Providing healthcare-specific tools validated by in-house doctors
* Enabling secure access to real-time medication data and treatment protocols for the LLM

Key Benefits:
* 🩺 Medical Accuracy: Ground AI responses in verified healthcare information
* 🔄 Seamless Workflow: Access critical information without context switching
* 🛡️ Reduced Hallucinations: Rely on curated medical data rather than AI's general knowledge
* 🌐 Open Ecosystem: Part of the growing MCP open standard

# Get Started
## Get your developer key from eka.care
> You can obtain the `eka-api-host`, `client-id`, and `client-token` from developer.eka.care or reach out to us on support@eka.care

## Installation and Setup for Claude Desktop
1. Install UV - https://docs.astral.sh/uv/getting-started/installation/#installation-methods
2. Clone this repository
```bash
git clone https://github.com/eka-care/eka_mcp_server.git 
```
3. Install Claude desktop application - https://claude.ai/download
4. Locate the configuration file:
   - **macOS**: `/Library/Application\ Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

5. Modify the configuration file with the following settings:

```json
{
  "mcpServers": {
     ...
    "eka-mcp-server": {
      "command": "uv",
      "args": [
        "--directory",
        "<eka_mcp_server_folder_path>",
        "run",
        "eka_mcp_server",
        "--eka-api-host",
        "<eka_api_host>",
        "--client-id",
        "<client_id>",
        "--client-secret",
        "<client_secret>"
      ]
    }, 
     ...
  }
}
```
6. Replace the placeholder values:
   - `<eka_mcp_server_folder_path>`: Path to the folder containing the Eka MCP server
   - `<eka_api_host>`: Eka API host URL
   - `<client_id>`: Your client ID
   - `<client_secret>`: Your client secret

## Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging experience, we recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).

You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
npx @modelcontextprotocol/inspector uv --directory <eka_mcp_server_folder_path> run eka_assist
```
Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.

# Tools
> EKA MCP server tools are curated by the in-house doctors at eka.care and have been validated on an internal set of questionnaire 

## Medications tool suite
### Medication Understanding tool 
<details>
<summary>Tool definition here</summary>
https://github.com/eka-care/eka_mcp_server/blob/14ea2d17ac4d93e619583a4b719a925180d8ff7d/src/eka_assist/mcp_server.py#L113-L120
</details>

Access comprehensive information about drugs from a corpus of drugs based on the drug name or generic composition and filtered further through the drug form and volume.

![Medication Understanding](assets/medication_understanding.png)

APIs required for this tool
   - https://developer.eka.care/api-reference/eka_mcp/medications/search 

### Medication Interaction
<details>
<summary>Tool definition here</summary>
https://github.com/eka-care/eka_mcp_server/blob/14ea2d17ac4d93e619583a4b719a925180d8ff7d/src/eka_assist/mcp_server.py#L122-L126
</details>

Check for potential interactions between drugs based on the X,A,B,C,D severity levels 
   - ![Medication Interaction](assets/medication_interaction.png)

APIs required for this tool
   - https://developer.eka.care/api-reference/eka_mcp/medications/search - to get the generic composition of the drug name to check for interactions
   - https://developer.eka.care/api-reference/eka_mcp/medications/interactions

## Treatment Protocols
<details>
<summary>Tool definition here</summary>
https://github.com/eka-care/eka_mcp_server/blob/14ea2d17ac4d93e619583a4b719a925180d8ff7d/src/eka_assist/mcp_server.py#L128-L174
</details>

Standardized guidelines, procedures, and decision pathways for healthcare professionals are published by medical bodies.
They serve as comprehensive roadmaps for clinical care, ensuring consistent and evidence-based treatment approaches.

Current Coverage:
* 175 medical conditions/tags
* 180 treatment protocols
* Multiple authoritative publishers

### Treatment Protocols Workflow
1. For any given query, the LLM has to decide if the tag is supported or not through [this API](http://developer.eka.care/api-reference/eka_mcp/protocols/tags). During the init of the tool, we fetch the supported conditions.
2. Then, for the given tag, the LLM has to get the publishers that address that tag through [this API](http://developer.eka.care/api-reference/eka_mcp/protocols/publishers_by_tag).
3. Finally, with the tag, publisher and query, we fetch the relevant information from the repository of publishers through [this API](http://developer.eka.care/api-reference/eka_mcp/protocols/search).

APIs required for this tool
1. http://developer.eka.care/api-reference/eka_mcp/protocols/tags
2. http://developer.eka.care/api-reference/eka_mcp/protocols/publishers_by_tag
3. http://developer.eka.care/api-reference/eka_mcp/protocols/search

![Tag Confirmation](assets/treatment_tags.png)
![Publisher Confirmation](assets/protocol_publishers.png)
![Treatment Protocol](assets/protocol_search.png)


### Bugs and Issue Reporting
Please report any issues or bugs on the GitHub issue tracker.

## FAQ
**Q: Can I use this without an eka.care account?**

A: No, you need valid API credentials from eka.care to access the medical information.

**Q: Is this service free?**

A: While the MCP server code is open-source, access to eka.care's APIs required valid credentials.

**Q: Which LLMs support MCP natively?**

A: Currently, Anthropic's Claude models have native MCP support and also Cursor and Windsurf applications.