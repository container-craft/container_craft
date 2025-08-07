import hashlib
from pathlib import Path
from typing import Optional

from container_craft_core.env import ContainerCraftEnv
from container_craft_core.logger import get_logger

logger = get_logger(__name__)

class Cache:
    def __init__(self, env: Optional[ContainerCraftEnv] = None):
        self.env = env or ContainerCraftEnv()
        self.cache_dir = self.env.get_path("MC_CACHE_DIR")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Initialized Cache at: {self.cache_dir}")

    def _hash(self, data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def get_cache_path(self, key: str) -> Path:
        return self.cache_dir / key

    def has(self, key: str) -> bool:
        exists = self.get_cache_path(key).exists()
        logger.debug(f"Cache {'hit' if exists else 'miss'} for key: {key}")
        return exists

    def get(self, key: str) -> Optional[bytes]:
        path = self.get_cache_path(key)
        if path.exists():
            logger.debug(f"Reading cache entry: {key}")
            return path.read_bytes()
        logger.debug(f"Cache entry missing: {key}")
        return None

    def set(self, key: str, data: bytes):
        path = self.get_cache_path(key)
        path.write_bytes(data)
        logger.debug(f"Wrote cache entry: {key}")

cache = Cache()
