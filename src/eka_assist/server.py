import argparse
import asyncio
import logging
import sys
from typing import Any

import mcp.server.stdio
from mcp.server import NotificationOptions
from mcp.server.models import InitializationOptions

from .eka_mcp import EkaMCP
from .mcp_server import initialize_mcp_server

def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.

    Args:
        logger: Logger instance for recording initialization progress

    Returns:
        Parsed command line arguments
    """
    logger = logging.getLogger("parse_arguments")
    logger.info("Validating server arguments ..")
    parser = argparse.ArgumentParser(description='Start MCP server')
    parser.add_argument('--eka-mcp-api', required=True, help='EKA MCP API URL')
    parser.add_argument('--eka-mcp-token', required=True, help='EKA MCP API token')

    return parser.parse_args()

def initialize_eka_client(logger, api_url: str, api_token: str) -> EkaMCP:
    """
    Initialize the EkaMCP client with appropriate connection pool settings.

    Args:
        api_url: The API URL for the EkaMCP service
        api_token: The API token for authentication
    Returns:
        Initialized EkaMCP client
    """
    pool_limits = {
        "max_connections": 4,
        "max_keepalive_connections": 2,
    }

    return EkaMCP(
        api_url=api_url,
        api_token=api_token,
        pool_limits=pool_limits,
        logger=logger
    )

async def main() -> None:
    """
    Main entry point for the application.
    """

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
    )
    file_handler = logging.FileHandler('app.log')
    file_handler.setLevel(logging.DEBUG)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    logger = logging.getLogger("main")

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


    logger.info("Starting Eka MCP server ..")

    try:
        # Parse command line arguments
        args = parse_arguments()

        # Initialize the EkaMCP client
        eka_mcp = initialize_eka_client(
            logger=logger,
            api_url=args.eka_mcp_api,
            api_token=args.eka_mcp_token,
        )

        # Initialize and run the MCP server
        server, init_options = initialize_mcp_server(eka_mcp, logger)
        logger.info(f"This is the server {server}")
        # await handle_stdio(server, init_options)
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="eka_assist",
                    server_version="0.1.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
        logger.info(f"Server started: {init_options.server_name} v{init_options.server_version}")

    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        sys.exit(1)
    finally:
        logger.info("Server shutdown complete")