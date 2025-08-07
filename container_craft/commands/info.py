import argparse
from container_craft.context import context
from container_craft.libcore import logger, error_handler

def show_info(args):
    """Show container status, networking, and other info.

    This command displays detailed information about the configured Minecraft server containers,
    including their network settings and status.
    """
    try:
        config = context.load()
        servers = config.get("servers", {})
        for server_name, server_config in servers.items():
            logger.info(f"Server: {server_name}")
            network = server_config.get("network", {})
            if network:
                logger.info(f"  Network: {network.get('name', 'N/A')}")
                logger.info(f"  IP Address: {network.get('ipaddress', 'N/A')}")
                logger.info(f"  Port: {network.get('port', 'N/A')}")
            else:
                logger.info("  No network info available.")
            logger.info("")
    except Exception as e:
        error_handler.handle_error("Failed to show info", e)
