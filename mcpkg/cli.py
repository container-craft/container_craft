import sys
import argparse
from container_craft_core.logger import logger

from mcpkg.commands.search import search

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

def parse_commands():
    parser = argparse.ArgumentParser(
        prog="mcpkg",
        description="Welcome to MCPkg CLI - Minecraft Package Manager"
    )
    command_parser = parser.add_subparsers(dest="command", help="subcommands help")

    # --- search subcommand ---
    search_parser = command_parser.add_parser("search", help="Search for mods from a provider")    
    search.args(search_parser)






    # --- other stubs ---
    command_parser.add_parser("create", help="Create a repo or package (TODO).")
    command_parser.add_parser("install", help="Install a package (TODO).")
    command_parser.add_parser("list", help="List packages (TODO).")
    command_parser.add_parser("remove", help="Remove a package (TODO).")
    command_parser.add_parser("update", help="Update package metadata (TODO).")
    command_parser.add_parser("upgrade", help="Upgrade packages (TODO).")
    command_parser.add_parser("verify", help="Verify signatures (TODO).")


    # parse the main parser now that we have the subcommands set up
    args = parser.parse_args()
    if args.command == "search":
        return search.run(search_parser)
    
    elif args.command in COMMANDS:
        logger.warning(f"Command '{args.command}' not yet implemented.")
        parser.print_help()
        return 2


    logger.warning(f"Command '{args.command}' not yet implemented.")
