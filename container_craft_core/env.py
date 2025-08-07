import os
from pathlib import Path
from typing import Optional, Dict, Any


# Default values — lowest precedence
BASE_DEFAULTS = {
    # Minecraft runtime/build settings
    "MC_VERSION": None,
    "MC_MEMORY": "4G",
    "MC_BASE": "/home/mc",
    "MC_PORT": "25565",

    # Container Craft core paths
    "MC_WORK_DIR": os.getcwd(),
    "VELOCITY_FILES": "",

    # Optional
    "SSH_PRIVATE_KEY": None,

    # SSH agent runtime support
    "SSH_AUTH_SOCK": None,
    "SSH_AGENT_PID": None,
    "SSH_ASKPASS": None,

    "CURSE_FORGE_KEY": None,
}

def derived_defaults(work_dir: str) -> Dict[str, str]:
    return {
        "MC_BUILD_DIR": os.path.join(work_dir, "build"),
        "MC_DOWNLOADS_DIR": os.path.join(work_dir, "downloads"),
        "MC_CACHE_DIR": os.path.join(work_dir, "cache"),
        "MC_LAYERS_DIR": os.path.join(work_dir, "build", "layers"),
        "MC_CONFIG": os.path.join(work_dir, ".config.yml"),
    }

ALL_KNOWN_VARS = set(BASE_DEFAULTS.keys()) | {
    "MC_BUILD_DIR",
    "MC_DOWNLOADS_DIR",
    "MC_CACHE_DIR",
    "MC_LAYERS_DIR",
    "MC_CONFIG",
}


class ContainerCraftEnv:
    def __init__(self, config_defaults: Optional[Dict[str, Any]] = None, cli_args: Optional[Dict[str, Any]] = None):
        self.config_defaults = config_defaults or {}
        self.cli_args = cli_args or {}

        self.work_dir = self._get_raw("MC_WORK_DIR")
        self._defaults = {
            **BASE_DEFAULTS,
            **derived_defaults(self.work_dir),
        }

    def _get_raw(self, key: str) -> Optional[str]:
        # Priority: CLI > config > os.environ > base defaults
        if key in self.cli_args:
            return self.cli_args[key]
        if key in self.config_defaults:
            return self.config_defaults[key]
        if key in os.environ:
            return os.environ[key]
        return self._defaults.get(key)

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        if key not in ALL_KNOWN_VARS:
            raise KeyError(f"Unknown ContainerCraft environment key: '{key}'")
        return self._get_raw(key) or default

    def get_path(self, key: str) -> Path:
        return Path(self.get(key))

    def get_list(self, key: str, separator: str = ",") -> list:
        return [x.strip() for x in self.get(key, "").split(separator) if x.strip()]

    def as_dict(self) -> Dict[str, str]:
        return {k: self.get(k) for k in ALL_KNOWN_VARS}

    def dump(self) -> str:
        return "\n".join(f"{k}: {self.get(k)}" for k in sorted(ALL_KNOWN_VARS))
