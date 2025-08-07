import argparse
import subprocess
from container_craft.libcore import logger, error_handler

def attach(args):
    """Drop into a Minecraft console session via tmux."""
    try:
        subprocess.run(["tmux", "attach-session", "-t", args.image_name], check=True)
    except subprocess.CalledProcessError:
        logger.error(f"Failed to attach to tmux session for container {args.image_name}")
        error_handler.handle_error(f"Failed to attach to tmux session for container {args.image_name}")
