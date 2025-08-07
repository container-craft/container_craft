import argparse
import subprocess
from container_craft.libcore import logger, error_handler

def tail_logs(args):
    """Tail the Minecraft server logs inside a Docker container."""
    try:
        subprocess.run(["docker", "logs", "-f", args.image_name], check=True)
    except subprocess.CalledProcessError:
        logger.error(f"Failed to tail logs for container {args.image_name}")
        error_handler.handle_error(f"Failed to tail logs for container {args.image_name}")
