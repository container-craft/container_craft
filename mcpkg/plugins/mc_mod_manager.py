import os
from pathlib import Path
import httpx

## fixme use the new paths

from container_craft_core import logger, error_handler, cache
from mcpkg.plugins import curse_forge, ftb, hangar, modrith

class ModManager:
    def __init__(self, mods_dir: str = None):
        self.mods_dir = Path(mods_dir) if mods_dir else Path("./mods")
        self.mods_dir.mkdir(parents=True, exist_ok=True)
        self.managers = {
            "curseforge": curse_forge,
            "ftb": ftb,
            "hangar": hangar,
            "modrith": modrith,
        }

    def resolve_mods(self, mod_list):
        resolved_mods = {}
        for mod in mod_list:
            if isinstance(mod, str):
                # Assume mod slug or local file path
                resolved_mods[mod] = mod
            elif isinstance(mod, dict):
                # Handle dict mod definitions
                mod_name = mod.get("name", "unknown_mod")
                mod_path = mod.get("path")
                resolved_mods[mod_name] = mod_path
            else:
                logger.warning(f"Unknown mod definition type: {mod}")
        return resolved_mods

    def merge_mods(self, base_mods, override_mods):
        merged = list(base_mods)
        for mod in override_mods:
            if mod not in merged:
                merged.append(mod)
        return merged

    def validate_mods(self, mods):
        for mod in mods:
            if not isinstance(mod, (str, dict)):
                error_handler.handle_error(f"Invalid mod definition: {mod}")
            if isinstance(mod, dict) and "slug" not in mod:
                error_handler.handle_error(f"Mod dict missing 'slug' key: {mod}")

    def cache_mod(self, mod_slug, mod_data):
        # Cache mod data by slug
        cache.set(mod_slug, mod_data)

    def download_mod_file(self, url: str, filename: str, modloader: str, mc_version: str):
        # Cache downloads in modloader/mc_version folder
        modloader_dir = self.mods_dir / modloader / mc_version
        modloader_dir.mkdir(parents=True, exist_ok=True)
        file_path = modloader_dir / filename
        if file_path.exists():
            logger.info(f"Mod file {filename} already cached.")
            return file_path
        try:
            with httpx.stream("GET", url) as response:
                response.raise_for_status()
                with file_path.open("wb") as f:
                    for chunk in response.iter_bytes():
                        f.write(chunk)
            logger.info(f"Downloaded mod file {filename} to {file_path}")
            return file_path
        except Exception as e:
            error_handler.handle_error(f"Failed to download mod file {url}", e)

    def download_mod_to_server(self, server_name: str, url: str, filename: str, modloader: str, mc_version: str):
        # Define the server-specific mods directory
        server_mods_dir = Path(f"build/{server_name}/mods") / modloader / mc_version
        server_mods_dir.mkdir(parents=True, exist_ok=True)
        file_path = server_mods_dir / filename

        if file_path.exists():
            logger.info(f"Mod file {filename} already exists in {server_mods_dir}.")
            return file_path

        try:
            with httpx.stream("GET", url) as response:
                response.raise_for_status()
                with file_path.open("wb") as f:
                    for chunk in response.iter_bytes():
                        f.write(chunk)
            logger.info(f"Downloaded mod file {filename} to {file_path}")
            return file_path
        except Exception as e:
            error_handler.handle_error(f"Failed to download mod file {url} to server {server_name}", e)

    def get_manager(self, manager_name):
        return self.managers.get(manager_name)

mod_manager = ModManager()
