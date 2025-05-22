import json
from logging import Logger

import mcp.types as types
from mcp.server import Server
from typing import List

from .constants import (
    INDIAN_BRANDED_DRUG_SEARCH,
    INDIAN_TREATMENT_PROTOCOL_SEARCH, PROTOCOL_PUBLISHERS_DESC,
    SNOMED_LINKER_DESC, PHARMACOLOGY_SEARCH_DESC
)
from .eka_client import EkaCareClient
from .models import IndianBrandedDrugSearch, QueryProtocols, ProtocolPublisher, SnomedLinker, PharmacologySearch
from .utils import download_image


def initialize_mcp_server(client: EkaCareClient, logger: Logger):
    # Store notes as a simple key-value dict to demonstrate state management
    server = Server("eka-mcp-server")

    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """
        List available tools.
        Each tool specifies its arguments using JSON Schema validation.
        """
        logger.info("Listing tools now")
        tags = client.get_supported_tags()

        return [
            types.Tool(
                name="snomed_linker",
                description=SNOMED_LINKER_DESC,
                inputSchema=SnomedLinker.model_json_schema(mode="serialization"),
            ),
            types.Tool(
                name="indian_branded_drug_search",
                description=INDIAN_BRANDED_DRUG_SEARCH,
                inputSchema=IndianBrandedDrugSearch.model_json_schema(
                    mode="serialization"
                ),
            ),
            types.Tool(
                name="indian_treatment_protocol_search",
                description=INDIAN_TREATMENT_PROTOCOL_SEARCH.format(tags=', '.join(tags)),
                inputSchema=QueryProtocols.model_json_schema(mode="serialization")
            ),
            types.Tool(
                name="protocol_publishers",
                description=PROTOCOL_PUBLISHERS_DESC.format(', '.join(tags)),
                inputSchema=ProtocolPublisher.model_json_schema(mode="serialization"),
            ),
            types.Tool(
                name="pharmacology_search",
                description=PHARMACOLOGY_SEARCH_DESC.format(', '.join(tags)),
                inputSchema=PharmacologySearch.model_json_schema(mode="serialization"),
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
            "indian_branded_drug_search": _handle_indian_branded_drug_search,
            "indian_treatment_protocol_search": _handle_indian_treatment_protocol_search,
            "protocol_publishers": _handle_protocol_publishers,
            "snomed_linker" : _handle_snomed_linker,
            "pharmacology_search": _handle_pharmacology_search
        }

        if name not in tool_handlers:
            raise ValueError(f"Unknown tool: {name}")

        return await tool_handlers[name](arguments)

    # Helper functions for tool handlers
    async def _handle_indian_branded_drug_search(arguments):
        drugs = client.get_suggested_drugs(arguments)
        return [types.TextContent(type="text", text=json.dumps(drugs))]


    async def _handle_indian_treatment_protocol_search(arguments):
        protocols = client.get_protocols(arguments)
        output = []
        for protocol in protocols:
            url = protocol.get("url")
            try:
                data = download_image(url)
                output.append(
                    types.ImageContent(
                        type="image",
                        data=data,
                        mimeType="image/jpeg",

                        # TODO: this can be used by LLM to generate a better response
                        url=url,
                        publisher=protocol.get("author"),
                        publication_year=protocol.get("publication_year"),
                        source_url=protocol.get("source_url"),
                    )
                )
            except Exception as err:
                logger.error(f"Failed to download protocol url: {protocol.get('url')}, with error: {err}")
        return output

    async def _handle_protocol_publishers(arguments):
        publishers = client.get_protocol_publisher(arguments)
        return [types.TextContent(type="text", text=json.dumps(publishers))]

    async def _handle_snomed_linker(arguments: List[str]):
        response = client.get_snomed_linker(arguments)
        return [types.TextContent(type="text", text=json.dumps(response))]
    
    async def _handle_pharmacology_search(arguments):
        response = client.get_pharmacology_search(arguments)
        return [types.TextContent(type="text", text=json.dumps(response))]
    
    return server
