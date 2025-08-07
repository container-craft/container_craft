import sys
import argparse
from importlib import import_module
from container_craft_core.logger import logger

# All supported top-level commands
COMMANDS = {
    "create",
    "install",
    "list",
    "remove",
    "search",
    "update",
    "upgrade",
    "verify",
}

def parse_commands(parser):


    parser.add_argument("command", help="Command to run", choices=COMMANDS)
    parser.add_argument("extra", nargs=argparse.REMAINDER, help="Additional arguments passed to the subcommand")

    args = parser.parse_args()

    command_name = args.command
    extra_args = args.extra

    try:
        command_module = import_module(f"mcpkg.commands.{command_name}")
    except ImportError as e:
        logger.error(f"Unknown or unimplemented command: {command_name}")
        sys.exit(1)

    if not hasattr(command_module, "run"):
        logger.error(f"Command '{command_name}' does not implement a run() function.")
        sys.exit(1)

    try:
        command_module.run(extra_args)
    except Exception as e:
        logger.exception(f"Error while executing command '{command_name}': {e}")
        sys.exit(1)
