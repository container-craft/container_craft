import git
from pathlib import Path
import shutil
import os

from container_craft_core.env import ContainerCraftEnv
from container_craft_core.logging import get_logger
from container_craft_core.ssh_agent import ssh_agent

logger = get_logger("container_craft.layers")


class LayerManager:
    def __init__(self, env: ContainerCraftEnv):
        self.env = env
        self.layers_dir = Path(self.env.layers_dir)
        self.layers_dir.mkdir(parents=True, exist_ok=True)
        self.ssh_key = self.env.ssh_key

        if self.ssh_key:
            ssh_agent.add_key(self.ssh_key)

        logger.debug(f"Initialized LayerManager with layers_dir: {self.layers_dir}, ssh_key: {self.ssh_key}")

    def clone_or_update_layer(self, name: str, url: str, branch: str = None, commit: str = None, path: str = None) -> Path:
        """
        Clone or update a layer from Git.
        - name: logical name of the layer
        - url: Git URL
        - branch: optional branch
        - commit: optional pinned commit
        - path: override the target folder name inside layers_dir
        """
        target_path = self.layers_dir / (path or name)
        logger.debug(f"Target repo path: {target_path}")

        if target_path.exists():
            logger.debug(f"Repo already exists. Updating: {target_path}")
            repo = git.Repo(target_path)
            origin = repo.remotes.origin
            origin.fetch()

            if branch:
                logger.debug(f"Checking out branch: {branch}")
                repo.git.checkout(branch)
                repo.git.pull("origin", branch)

            if commit:
                logger.debug(f"Checking out commit: {commit}")
                repo.git.checkout(commit)

        else:
            logger.debug(f"Cloning from {url} to {target_path}")
            repo = git.Repo.clone_from(url, target_path)

            if branch:
                logger.debug(f"Checking out branch after clone: {branch}")
                repo.git.checkout(branch)

            if commit:
                logger.debug(f"Checking out commit after clone: {commit}")
                repo.git.checkout(commit)

        return target_path

    def update_layers(self, layers_config: dict):
        """
        Takes a dictionary like:
        layers:
          my_layer:
            url: git@github.com:me/repo.git
            branch: main
            commit: abc123
            path: optional/custom-path
        """
        if not layers_config:
            logger.info("No layers to update — skipping (possibly base modloader)")
            return

        logger.debug(f"Starting layer update: {layers_config.keys()}")

        for name, layer in layers_config.items():
            url = layer.get("url")
            branch = layer.get("branch")
            commit = layer.get("commit")
            path = layer.get("path")

            if not url:
                logger.warning(f"Skipping layer '{name}' — missing 'url'")
                continue

            logger.debug(f"Updating layer: {name}")
            self.clone_or_update_layer(name, url, branch, commit, path)


def get_layers_dir(context: dict) -> Path:
    """Returns the directory where Git layers are stored (creates it if needed)."""
    layers_dir = context.get("defaults", {}).get("layers_dir", "./build/layers")
    logger.debug(f"Resolved layers_dir: {layers_dir}")
    path = Path(layers_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_build_dir(context: dict) -> Path:
    """Returns the build directory path."""
    build_dir = context.get("defaults", {}).get("build_dir", f"{os.getcwd()}/build")
    logger.debug(f"Resolved build_dir: {build_dir}")
    path = Path(build_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path
