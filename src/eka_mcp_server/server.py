import argparse

import logging

import mcp.server.stdio
from eka_mcp_server.eka_client import EkaCareClient
from mcp.server import NotificationOptions
from mcp.server.models import InitializationOptions

# from .eka_client import EkaCareClient
from eka_mcp_server.mcp_server import initialize_mcp_server


async def main() -> None:
    """
    Main entry point for the application.
    """

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )

    logger = logging.getLogger("main")
    logger.info("Starting Eka MCP server..")

    logger.info("Validating server arguments..")
    parser = argparse.ArgumentParser(
        description="Eka MCP server. Documentation available at - https://github.com/eka-care/eka_mcp_server/blob/main/README.md"
    )
    parser.add_argument("--eka-api-host", required=True, help="EKA MCP API Host")
    parser.add_argument("--client-id", required=False, help="EKA MCP API Client ID")
    parser.add_argument("--client-secret", required=False, help="EKA MCP Client Secret")

    args = parser.parse_args()
    # Initialize the EkaMCP client
    eka_mcp = EkaCareClient(
        eka_api_host=args.eka_api_host,
        client_id=args.client_id,
        client_secret=args.client_secret,
        logger=logger,
    )

    # Initialize and run the MCP server
    server = initialize_mcp_server(eka_mcp, logger)

    # await handle_stdio(server, init_options)
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="eka_mcp_server",
                server_version="0.3.5",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
    logger.info(f"Eka MCP Server started")
