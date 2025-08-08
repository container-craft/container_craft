import os
import json
import yaml
from pathlib import Path

from container_craft_core.config.schema_validator import SchemaValidator
from container_craft_core.env import ContainerCraftEnv
from container_craft_core.error_handler import error_handler
from container_craft_core.logger import get_logger

logger = get_logger("context")

class Context:
    def __init__(self, config_paths: str = None):
        self.env = ContainerCraftEnv()

        # Determine initial config paths (CLI override or fallback to env/derived)
        default_path = self.env.get("MC_CONFIG")
        self.config_paths = config_paths.split(":") if config_paths else [default_path]

        # FIFO: base config is loaded last, later entries override earlier ones
        self._raw_paths = list(self.config_paths)
        self.config = None

    def load(self):
        logger.debug(f"Initial config paths: {self.config_paths}")

        # MC_INCLUDE_* variables get added to the front (highest priority)
        includes = self.env.get_list("MC_INCLUDE_PRE") + list(self._raw_paths)

        merged_config = {}

        visited = set()
        while includes:
            path_str = includes.pop(0)
            path = Path(path_str).expanduser().resolve()

            if path in visited:
                logger.debug(f"Already loaded: {path}")
                continue
            visited.add(path)

            if not path.exists():
                logger.warning(f"Skipping non-existent config: {path}")
                continue

            logger.debug(f"Loading config from {path}")
            try:
                with path.open("r") as f:
                    if path.suffix == ".json":
                        config_part = json.load(f)
                    else:
                        config_part = yaml.safe_load(f)
                    config_part = config_part or {}
            except Exception as e:
                error_handler.handle_error(f"Failed to parse config file: {path}", e)

            # FIFO: base config is loaded last
            merged_config = self._deep_merge(merged_config, config_part)

            # Includes from within the file
            new_includes = config_part.get("includes", [])
            for include in new_includes:
                include_path = Path(include).expanduser()
                if not include_path.is_absolute():
                    include_path = path.parent / include_path
                includes.append(str(include_path))

        # Validate against schema
        SchemaValidator().validate(merged_config)

        # Inject env (lowest priority, unless overridden)
        merged_config.setdefault("defaults", {})
        merged_config["defaults"].setdefault("env", {})
        merged_config["defaults"]["env"].update(self.env.as_dict())

        self.config = merged_config
        return self.config

    def get(self, *keys, default=None):
        """
        Access nested configuration keys.
        Example: context.get("defaults", "build_dir")
        """
        current = self.config
        for key in keys:
            if not isinstance(current, dict):
                return default
            current = current.get(key, default)
        return current

    def dump(self, fmt: str = "yaml", json_indent: int = 2) -> str:
        """
        Dump the currently loaded merged config (must call `load()` first).
        """
        if self.config is None:
            raise RuntimeError("Cannot dump — config not loaded")

        fmt = fmt.lower()
        if fmt == "yaml":
            return yaml.safe_dump(self.config, sort_keys=False)
        elif fmt == "json":
            return json.dumps(self.config, indent=json_indent)
        else:
            raise ValueError("Format must be 'yaml' or 'json'")

    def _deep_merge(self, base: dict, override: dict) -> dict:
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                base[key] = self._deep_merge(base[key], value)
            else:
                base[key] = value
        return base


# Global singleton for shared access
context = Context()
