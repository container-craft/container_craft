from pathlib import Path
from typing import Optional

from mcpkg.plugins.modrith import ModrinthClient
from container_craft_core.logger import get_logger
from container_craft_core.config.context import context
from container_craft_core.env import ContainerCraftEnv

logger = get_logger("mcpkg_search")


def exec(
    provider: Optional[str] = None,
    package_name: Optional[str] = None,
    version: Optional[str] = None,
    config_path: Optional[str] = None
) -> int:
    if config_path:
        logger.info(f"Loading config from {config_path}")
        context.config_paths = config_path.split(":")
        cfg = context.load()

        provider_blocks = context.get("servers", default={})
        if not provider_blocks:
            logger.error("No 'servers' block found in configuration.")
            return 1

        for server_name, server_entry in provider_blocks.items():
            logger.info(f"Searching mods for server: {server_name}")
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
                        logger.warning(f"Invalid mod entry: {mod_entry}")
                        continue

                    logger.info(f"→ Searching: {mod_slug} (provider: {provider_key}, version: {mod_version})")
                    _search_single(provider_key, mod_slug, mod_version)

        return 0

    # If no config path, use explicit CLI args
    if not provider or not package_name:
        logger.error("Either --provider and --mod must be set, or a config path must be provided.")
        return 2

    # Use raw env for MC_VERSION fallback
    env = ContainerCraftEnv()
    resolved_version = version or env.get("MC_VERSION")
    return _search_single(provider, package_name, resolved_version)


def _search_single(provider: str, package_name: str, version: Optional[str] = None) -> int:
    logger.info(f"Searching for '{package_name}' from provider '{provider}' (version={version})")

    if provider == "modrith":
        client = ModrinthClient()
        try:
            mod_version = client.do_search(package_name, version)

            print(f"\n✅ Found: {mod_version['name']} ({mod_version['version_number']})")
            print(f"  - MC Versions: {mod_version['game_versions']}")
            print(f"  - Loaders: {mod_version['loaders']}")
            print(f"  - Dependencies: {len(mod_version.get('dependencies', []))}")
            print(f"  - File: {mod_version['files'][0]['filename']}")
            print(f"  - Download: {mod_version['files'][0]['url']}")
            return 0

        except Exception as e:
            logger.error(f"Modrinth search failed: {e}")
            return 1

    elif provider == "curse_forge":
        logger.warning("CurseForge search is not yet implemented.")
        return 2

    elif provider == "hangar":
        logger.warning("Hangar search is not yet implemented.")
        return 3

    elif provider == "local":
        logger.warning("Local search is not supported. Skipping.")
        return 4

    else:
        logger.error(f"Unknown provider '{provider}'.")
        return 5
