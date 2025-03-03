import argparse
import sys

import logging
from logging.handlers import RotatingFileHandler

import mcp.server.stdio
from mcp.server import NotificationOptions
from mcp.server.models import InitializationOptions

from .eka_mcp import EkaMCP
from .mcp_server import initialize_mcp_server


async def main() -> None:
    """
    Main entry point for the application.
    """

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            RotatingFileHandler(
                "app.log",
                maxBytes=10485760,
                backupCount=5,
                encoding="utf-8"
            )
        ]
    )

    logger = logging.getLogger("main")
    logger.info("Starting Eka MCP server ..")

    try:
        logger.info("Validating server arguments ..")
        parser = argparse.ArgumentParser(description='Start MCP server')
        parser.add_argument('--eka-mcp-host', required=True, help='EKA MCP API HOST - see developer.eka.care for more information')
        parser.add_argument('--eka-mcp-token', required=True, help='EKA MCP API token')

        args = parser.parse_args()

        pool_limits = {
            "max_connections": 4,
            "max_keepalive_connections": 2,
        }
        # Initialize the EkaMCP client
        eka_mcp = EkaMCP(
            api_url=args.eka_mcp_host,
            api_token=args.eka_mcp_token,
            pool_limits=pool_limits,
            logger=logger
        )

        # Initialize and run the MCP server
        server = initialize_mcp_server(eka_mcp, logger)
        logger.info(f"Server created successfully: {server}")

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
        logger.info(f"Eka Mcp Server started ...")

    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        sys.exit(1)
    finally:
        logger.info("Server shutdown complete")
