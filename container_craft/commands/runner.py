import argparse
from container_craft.context import context
from container_craft.docker import Docker
import subprocess
from container_craft.libcore import logger, error_handler
import shutil
import zipfile
import logging
import os
import sys
from pathlib import Path

docker = Docker()

print('runner.py loaded successfully')


def cleanup_container(name: str):
    try:
        existing = subprocess.run(["docker", "ps", "-a", "--format", "{{.Names}}"], capture_output=True, text=True)
        if name in existing.stdout.splitlines():
            logger.info(f"Removing existing container: {name}")
            subprocess.run(["docker", "rm", "-f", name], check=True)
    except Exception as e:
        logger.error(f"Failed to cleanup container {name}: {e}")


def recreate_network(network_name: str, subnet: str, gateway: str):
    try:
        existing = subprocess.run(["docker", "network", "inspect", network_name], capture_output=True, text=True)
        if existing.returncode == 0:
            logger.info(f"Removing existing network: {network_name}")
            subprocess.run(["docker", "network", "rm", network_name], check=True)
        logger.info(f"Creating Docker network: {network_name}")
        subprocess.run([
            "docker", "network", "create",
            "--subnet", subnet,
            "--gateway", gateway,
            network_name
        ], check=True)
    except Exception as e:
        error_handler.handle_error(f"Failed to recreate network {network_name}", e)


def extract_world_zip(zip_path: Path, extract_to: Path):
    if extract_to.exists():
        shutil.rmtree(extract_to)
    extract_to.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)


def run(args):
    """Run a Minecraft server container."""
    try:
        # Check /srv/minecraft/ folder
        srv_path = "/srv/minecraft"
        if not os.path.exists(srv_path):
            logger.error(f"Required directory {srv_path} does not exist.")
            sys.exit(1)
        if not os.access(srv_path, os.R_OK | os.W_OK):
            logger.error(f"Insufficient permissions on {srv_path}. Must be readable and writable.")
            sys.exit(1)

        config = context.load()
        servers = config.get("servers", {})
        server_config = servers.get(args.image_name)
        if not server_config:
            error_handler.handle_error(f"Image {args.image_name} not found in config.")

        network = server_config.get("network", {})
        if network:
            recreate_network(network.get("name"), network.get("subnet", "172.18.0.0/16"), network.get("gateway", "172.18.0.1"))

        container_name = args.image_name
        cleanup_container(container_name)

        ports = []
        if network:
            port = network.get("port")
            if port:
                ports.append(f"{port}:{port}")

        env = server_config.get("env", {})

        volumes = []
        world = server_config.get("world", {})
        if world:
            host_path = world.get("host")
            file_path = world.get("file")
            if host_path:
                volumes.append(f"{host_path}:/home/mc/world")
            elif file_path:
                zip_path = Path(file_path)
                extract_dir = Path("./extracted_worlds") / args.image_name
                extract_world_zip(zip_path, extract_dir)
                volumes.append(f"{extract_dir}:/home/mc/world")

        ip_address = network.get("ipaddress") if network else None

        success = docker.run_container(
            image=args.image_name,
            name=container_name,
            detach=True,
            ports=ports,
            env=env,
            volumes=volumes,
            command=None
        )

        if not success:
            error_handler.handle_error(f"Failed to run container for image {args.image_name}")

        print(f"Container for image {args.image_name} started successfully.")
        print(f"Debug: Container for image {args.image_name} started successfully.")
        print(f"Logger Handlers: {logger.handlers}")
        print(f"Logger Name: {logger.name}")
        logger.info(f"Container for image {args.image_name} started successfully.")
        for handler in logger.handlers:
            handler.flush()
    except Exception as e:
        error_handler.handle_error("Run command failed", e)
    finally:
        logger.addHandler(logging.StreamHandler(sys.stdout))


def stop(container_name: str):
    """Stop a running Minecraft server container.

    This command stops the specified Docker container running a Minecraft server.

    Args:
        container_name (str): Name of the container to stop.
    """
    try:
        subprocess.run(["docker", "stop", container_name], check=True)
        logger.info(f"Container {container_name} stopped successfully.")
    except subprocess.CalledProcessError:
        error_handler.handle_error(f"Failed to stop container {container_name}")


def start(container_name: str):
    """Start a Minecraft server container.

    This command starts the specified Docker container running a Minecraft server.

    Args:
        container_name (str): Name of the container to start.
    """
    try:
        subprocess.run(["docker", "start", container_name], check=True)
        logger.info(f"Container {container_name} started successfully.")
    except subprocess.CalledProcessError:
        error_handler.handle_error(f"Failed to start container {container_name}")


