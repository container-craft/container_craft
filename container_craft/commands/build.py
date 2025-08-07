import argparse
import os
import yaml
from container_craft.docker import Docker
from container_craft.ssh_agent import ssh_agent
from container_craft.logger import logger error_handler
from container_craft.config.context import context
from container_craft.config.layers import LayerManager, get_layers_dir, get_build_dir

from container_craft.mods import mod_manager

from container_craft.mc_loader_manager import ModLoaderManager
from container_craft.mc_mod_manager import ModManager

from pathlib import Path
import shutil
from container_craft.context_manager import load_context
from jinja2 import Environment, FileSystemLoader
import traceback

print("Debug: Initializing build_command...")

docker = Docker()
mod_loader_manager = ModLoaderManager()
mod_manager_instance = ModManager()

# Initialize Jinja2 environment
jinja_env = Environment(loader=FileSystemLoader('container_craft/templates'))
dockerfile_template = jinja_env.get_template('dockerfile_template.j2')


def prepare_build_directory(server_name, server_config, build_dir, mod_manager_instance):
    """Prepare the build directory for the server."""
    # Create mods directory and download mods
    mods_dir = build_dir / "mods"
    mods_dir.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Mods directory created: {mods_dir}")

    resolved_mods = mod_manager_instance.resolve_mods(server_config.get("mods", {}))
    logger.debug(f"Resolved mods: {resolved_mods}")

    for mod_name, mod_path in resolved_mods.items():
        logger.debug(f"Processing mod: {mod_name}, path: {mod_path}")
        if mod_path is None:
            logger.error(f"Mod path for {mod_name} is None. Skipping...")
            continue
        if not Path(mod_path).exists():
            logger.error(f"Mod path for {mod_name} does not exist: {mod_path}. Skipping...")
            continue
        shutil.copy(mod_path, mods_dir / Path(mod_path).name)

    # Create config directory and copy config files
    config_dir = build_dir / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_files = server_config.get("config_files", [])
    for cf in config_files:
        src = Path(cf)
        if src.exists():
            shutil.copy(src, config_dir / src.name)

    # Copy entry point script if defined
    entry_point = server_config.get("entry_point")
    if entry_point:
        entry_point_path = Path(entry_point)
        if entry_point_path.exists():
            shutil.copy(entry_point_path, build_dir / "entry_point.sh")

    return resolved_mods






def build_all(args):
    try:
        if args.ssh_key:
            ssh_agent.add_key(args.ssh_key)

        logger.debug("Loading context from configuration files...")
        combined_config = load_context(args.yaml_files)
        logger.debug(f"Combined configuration: {combined_config}")

        layers_dir = get_layers_dir(combined_config)
        if not layers_dir.exists():
            layers_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Resolved layers directory: {layers_dir}")

        servers = combined_config.get("servers", {})
        for server_name, server_config in servers.items():
            build_dir = get_build_dir(combined_config) / server_name
            build_dir.mkdir(parents=True, exist_ok=True)

            resolved_mods = prepare_build_directory(server_name, server_config, build_dir, mod_manager_instance)

            modloader_module = mod_loader_manager.get_loader(server_config.get("modloader"))
            modloader_fetch_command = modloader_module.do_fetch(combined_config.get("defaults", {}).get("env", {}).get("MINECRAFT_VERSION", "1.21.6"))
            modloader_install_command = modloader_module.do_install()

            dockerfile_content = dockerfile_template.render(
                parent_image=server_config['parent_image'],
                env={**combined_config.get("defaults", {}).get("env", {}), **server_config.get("env", {})},
                modloader=server_config.get("modloader"),
                modloader_fetch_command=modloader_fetch_command,
                modloader_install_command=modloader_install_command,
                mods=resolved_mods,
                plugins=server_config.get("plugins", []),
                config_files=server_config.get("config_files", [])
            )

            dockerfile_path_generated = build_dir / "Dockerfile"
            with open(dockerfile_path_generated, "w") as df:
                df.write(dockerfile_content)

            tag = f"{server_name}:{server_config.get('version', 'latest')}"
            build_args = server_config.get("docker_args", {})
            success = docker.build_image(str(dockerfile_path_generated), tag, build_args, context_dir=str(build_dir))
            if not success:
                error_handler.handle_error(f"Failed to build image {tag}")
        logger.info("All images built successfully.")
    except Exception as e:
        logger.error(f"Build process failed: {e}")
        logger.error("Traceback:")
        logger.error(traceback.format_exc())
        error_handler.handle_error("Build process failed", e)

