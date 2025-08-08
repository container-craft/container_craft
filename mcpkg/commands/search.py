import sys
import importlib
import argparse
import os
from typing import Optional

from container_craft_core.logger import mcpkg_logger
from container_craft_core.config.context import context
from container_craft_core.env import env

from mcpkg.commands.mcpkg_abstract_commands import McPkgAbstractCommands


# from mcpkg.plugins.modrith import ModrinthClient
# from mcpkg.plugins.curse_forge import CurseForgeClient
# from mcpkg.plugins.modrith import ModrinthClient

class SearchCommand(McPkgAbstractCommands):
    def __init__(self):
        self.env = env

    @staticmethod
    def provider_to_class(name: str) -> str:
        """Map provider slug to class name."""
        return {
            "modrith": "ModrinthClient",
            "curse_forge": "CurseForgeClient",
            "hangar": "HangarClient",
        }.get(name, "")

    @staticmethod
    def _search_single(provider: str, package_name: str, version: Optional[str] = None) -> bool:
        # print(f"Searching for '{package_name}' from provider '{provider}' (version={version})")

        # this fails even though it is in the path
        try:
            plugin = importlib.import_module(f"mcpkg.plugins.{provider}")
        except ImportError:
            mcpkg_logger.error(f"Unknown provider '{provider}'.")
            return False

        provider_class_name = SearchCommand.provider_to_class(provider)
        if not hasattr(plugin, provider_class_name):
            mcpkg_logger.error(f"Provider plugin '{provider}' does not define expected class.")
            return False

        client_cls = getattr(plugin, provider_class_name)
        client = client_cls()

        if not hasattr(client, "do_search"):
            mcpkg_logger.error(f"Provider '{provider}' does not implement search().")
            return False

        try:
            results = client.do_search(package_name, version)
            if not results:
                mcpkg_logger.info("No results found.")
                return False
            if isinstance(results, dict):
                mod_name = results.get('name')
                mod_version = results.get('version_number')  # Assuming version_number is what you want
                game_versions = results.get('game_versions', [])
                loaders = results.get('loaders', [])
                author = results.get('author_id', 'Unknown')
                file_name = None
                download_url = None

                # Accessing file details if available (the first file in 'files' list)
                if results.get('files'):
                    file_data = results['files'][0]  # Assuming we want the first file
                    file_name = file_data.get('filename')
                    download_url = file_data.get('url')

                # Print the found details
                print(f"\nFound: {mod_name} ({mod_version})")
                print(f"  - MC Versions: {game_versions}")
                print(f"  - Loaders: {loaders}")
                print(f"  - Author: {author}")
                print(f"  - File: {file_name}")
                print(f"  - Download: {download_url}")

            return True  # Return after processing all results
        except Exception as e:
            mcpkg_logger.error(f"Search failed for provider '{provider}': {e}")
            return False

    @staticmethod
    def _search_from_config(config_path: str) -> bool:
        mcpkg_logger.info(f"Loading config from {config_path}")
        context.config_paths = config_path.split(":")
        cfg = context.load()

        provider_blocks = context.get("servers", default={})
        if not provider_blocks:
            mcpkg_logger.error("No 'servers' block found in configuration.")
            return False

        success = True
        for server_name, server_entry in provider_blocks.items():
            mcpkg_logger.info(f"Searching mods for server: {server_name}")
            mod_groups = server_entry.get("mcpkg", {})
            for provider_key, mods in mod_groups.items():
                for mod_entry in mods:
                    if isinstance(mod_entry, str):
                        mod_slug = mod_entry
                        mod_version = context.get("defaults", "env", "MC_VERSION")
                    elif isinstance(mod_entry, dict):
                        mod_slug, mod_spec = next(iter(mod_entry.items()))
                        mod_version = mod_spec.get("version", context.get("defaults", "env", "MC_VERSION"))
                    else:
                        mcpkg_logger.warning(f"Invalid mod entry: {mod_entry}")
                        success = False
                        continue

                    mcpkg_logger.info(f"→ Searching: {mod_slug} (provider: {provider_key}, version: {mod_version})")
                    if not SearchCommand._search_single(provider_key, mod_slug, mod_version):
                        success = False

        return success

    @staticmethod
    def args(subparser):
        subparser.add_argument(
            "-p", "--provider",
            help="Provider to search (modrith(default), curse_forge, hangar, local)",
            type=str,
            default="modrith"
        )
        subparser.add_argument(
            "-m", "--mod",
            help="Name or slug of the mod to search for",
            type=str,
            default=None
        )
        subparser.add_argument(
            "-v", "--version",
            help="Optional mod version to search",
            type=str,
            default="1.21.8"
        )
        subparser.add_argument(
            "-l", "--loader",
            help="ModLoader:  fabric(DEFAULT) forge neoforge paper velocity",
            type=str,
            default="fabric"
        )
        subparser.add_argument(
            "config_file",
            nargs="*",
            help="YAML or JSON config file",
            type=str,
            default=[]
        )

    @staticmethod
    def run(parser) -> bool:
        """
        Usage:
            mcpkg search --provider modrith --mod sodium --version 1.21.1
            mcpkg search /path/to/config.yml
        """
        # we need to shift one to the right in the args list because the config_file becaomes "search"
        # which is the 1st command and makes sense but we
        opts = parser.parse_args()
        resolved_version = opts.version or env.get("MC_VERSION")

        # os.environ['MC_LOADER'] = opts.loader
        # mcpkg_logger.debug(f" ")
        resoved_config = None
        if opts.config_file[0] == "search":
            resolved_config = opts.config_file[1:]  # Shift left if 'search' is the first arg

        # No arguments provided
        if not any(vars(opts).values()):
            if hasattr(opts, "print_help"):
                opts.print_help()
            return False

        # Config-based search
        if resolved_config:
            return SearchCommand._search_from_config(resolved_config)

        # Direct provider/mod search
        if not opts.mod:
            mcpkg_logger.error("--mod must be set, or a config file must be provided.")
            parser.print_help()
            return False
        return SearchCommand._search_single(opts.provider, opts.mod, resolved_version)

search = SearchCommand()
