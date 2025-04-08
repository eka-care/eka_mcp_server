import json
from logging import Logger

import mcp.types as types
from mcp.server import Server

from .constants import (
    MEDICATION_UNDERSTANDING_DESC,
    SEARCH_PROTOCOLS_DESC, PROTOCOL_PUBLISHERS_DESC
)
from .eka_interface import EkaMCP
from .models import MedicationUnderstanding, QueryProtocols, ProtocolPublisher
from .utils import download_image


def initialize_mcp_server(eka_mcp: EkaMCP, logger: Logger):
    # Store notes as a simple key-value dict to demonstrate state management
    server = Server("eka-mcp-server")

    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """
        List available tools.
        Each tool specifies its arguments using JSON Schema validation.
        """
        logger.info("Listing tools now")
        tags = eka_mcp.get_supported_tags()

        return [
            types.Tool(
                name="medication_understanding",
                description=MEDICATION_UNDERSTANDING_DESC,
                inputSchema=MedicationUnderstanding.model_json_schema(
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


    async def _handle_search_protocols(arguments):
        protocols = eka_mcp.get_protocols(arguments)
        output = []
        for protocol in protocols:
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
