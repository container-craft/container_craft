import argparse
import subprocess
from container_craft.libcore import logger, error_handler

def attach(args):
    """Attach to a running container with /bin/bash shell."""
    try:
        subprocess.run(["docker", "exec", "-it", args.container_name, "/bin/bash"], check=True)
    except subprocess.CalledProcessError:
        logger.error(f"Failed to attach shell to container {args.container_name}")
        error_handler.handle_error(f"Failed to attach shell to container {args.container_name}")


