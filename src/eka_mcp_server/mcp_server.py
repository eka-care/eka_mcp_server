import json
from logging import Logger

import mcp.types as types
from mcp.server import Server
from pydantic import AnyUrl

from .constants import (
    MEDICATION_UNDERSTANDING_DESC, MEDICATION_INTERACTION_DESC,
    SEARCH_PROTOCOLS_DESC, PROTOCOL_PUBLISHERS_DESC
)
from .eka_interface import EkaMCP
from .models import MedicationUnderstanding, MedicationInteraction, QueryProtocols, ProtocolPublisher
from .utils import download_image


def initialize_mcp_server(eka_mcp: EkaMCP, logger: Logger):
    # Store notes as a simple key-value dict to demonstrate state management

    notes: dict[str, str] = {}
    server = Server("eka-assist")

    @server.list_resources()
    async def handle_list_resources() -> list[types.Resource]:
        """
        List available note resources.
        Each note is exposed as a resource with a custom note:// URI scheme.
        """
        return [
            types.Resource(
                uri=AnyUrl(f"note://internal/{name}"),
                name=f"Note: {name}",
                description=f"A simple note named {name}",
                mimeType="text/plain",
            )
            for name in notes
        ]

    @server.read_resource()
    async def handle_read_resource(uri: AnyUrl) -> str:
        """
        Read a specific note's content by its URI.
        The note name is extracted from the URI host component.
        """
        if uri.scheme != "note":
            raise ValueError(f"Unsupported URI scheme: {uri.scheme}")

        name = uri.path
        if name is not None:
            name = name.lstrip("/")
            if name in notes:  # Added check for key existence
                return notes[name]
        raise ValueError(f"Note not found: {name}")

    @server.list_prompts()
    async def handle_list_prompts() -> list[types.Prompt]:
        """
        List available prompts.
        Each prompt can have optional arguments to customize its behavior.
        """
        return [
            types.Prompt(
                name="summarize-notes",
                description="Creates a summary of all notes",
                arguments=[
                    types.PromptArgument(
                        name="style",
                        description="Style of the summary (brief/detailed)",
                        required=False,
                    )
                ],
            )
        ]

    @server.get_prompt()
    async def handle_get_prompt(
            name: str, arguments: dict[str, str] | None
    ) -> types.GetPromptResult:
        """
        Generate a prompt by combining arguments with server state.
        The prompt includes all current notes and can be customized via arguments.
        """
        if name != "summarize-notes":
            raise ValueError(f"Unknown prompt: {name}")

        style = (arguments or {}).get("style", "brief")
        detail_prompt = " Give extensive details." if style == "detailed" else ""

        return types.GetPromptResult(
            description="Summarize the current notes",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Here are the current notes to summarize:{detail_prompt}\n\n"
                             + "\n".join(
                            f"- {name}: {content}"
                            for name, content in notes.items()
                        ),
                    ),
                )
            ],
        )

    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """
        List available tools.
        Each tool specifies its arguments using JSON Schema validation.
        """
        logger.info("Listing tools now")
        tags = eka_mcp.get_supported_tags()
        logger.info("Completed tools now")

        return [
            types.Tool(
                name="medication_understanding",
                description=MEDICATION_UNDERSTANDING_DESC,
                inputSchema=MedicationUnderstanding.model_json_schema(
                    mode="serialization"
                ),
            ),
            types.Tool(
                name="medication_interaction",
                description=MEDICATION_INTERACTION_DESC,
                inputSchema=MedicationInteraction.model_json_schema(
                    mode="serialization"
                ),
            ),
            types.Tool(
                name="search_protocols",
                description=SEARCH_PROTOCOLS_DESC.format(', '.join(tags)),
                inputSchema=QueryProtocols.model_json_schema(mode="serialization")
            ),
            types.Tool(
                name="protocol_publishers",
                description=PROTOCOL_PUBLISHERS_DESC.format(', '.join(tags)),
                inputSchema=ProtocolPublisher.model_json_schema(mode="serialization"),
            )
        ]

    @server.call_tool()
    async def handle_call_tool(
            name: str, arguments: dict | None
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """
        Handle tool execution requests.
        Tools can modify server state and notify clients of changes.
        """
        if not arguments:
            raise ValueError("Missing arguments")

        # Map tool names to handler functions for cleaner dispatching
        tool_handlers = {
            "medication_understanding": _handle_medication_understanding,
            "medication_interaction": _handle_medication_interaction,
            "search_protocols": _handle_search_protocols,
            "protocol_publishers": _handle_protocol_publishers
        }

        if name not in tool_handlers:
            raise ValueError(f"Unknown tool: {name}")

        return await tool_handlers[name](arguments)

    # Helper functions for tool handlers
    async def _handle_medication_understanding(arguments):
        drugs = eka_mcp.get_suggested_drugs(arguments)
        return [types.TextContent(type="text", text=json.dumps(drugs))]

    async def _handle_medication_interaction(arguments):
        interactions = eka_mcp.get_drug_interactions(arguments)
        return [types.TextContent(type="text", text=json.dumps(interactions))]

    async def _handle_search_protocols(arguments):
        protocols = eka_mcp.get_protocols(arguments)
        output = []
        for protocol in protocols:
            logger.info(f"Protocol: {protocol}")
            url = protocol.get("url")
            try:
                data = download_image(url)
                output.append(types.ImageContent(type="image", data=data, mimeType="image/jpeg"))
            except Exception as err:
                logger.error(f"Failed to download protocol url: {protocol.get('url')}, with error: {err}")
        return output

    async def _handle_protocol_publishers(arguments):
        publishers = eka_mcp.get_protocol_publisher(arguments)
        return [types.TextContent(type="text", text=json.dumps(publishers))]

    return server
