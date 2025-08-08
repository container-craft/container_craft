import os
import time
import httpx
from pathlib import Path
from typing import Optional

from mcpkg.plugins.api import McPkgApi
from container_craft_core.env import env
from container_craft_core.config.context import context
from container_craft_core.logger import mcpkg_logger
from container_craft_core.error_handler import error_handler
from container_craft_core.cache import cache

MODRINTH_API_BASE = "https://api.modrinth.com/v2"
USER_AGENT = "m_jimmer/container_craft/0.1.0 (m_jimmer@dontspamme.com)"

class ModrinthClient(McPkgApi):
    def __init__(self):
        self.env = env
        self.client = httpx.Client(
            base_url=MODRINTH_API_BASE,
            headers={"User-Agent": USER_AGENT}
        )
        self.last_call = 0
        self.rate_limit_interval = 60 / 300  # 300 requests/min = 1 every 0.2s

    def name(self) -> str:
        return "modrith"

    def base_url(self) -> str:
        return MODRINTH_API_BASE

    def key(self) -> Optional[str]:
        return None  # No API key required

    def _rate_limit(self):
        elapsed = time.time() - self.last_call
        if elapsed < self.rate_limit_interval:
            time.sleep(self.rate_limit_interval - elapsed)
        self.last_call = time.time()

    def do_search(self, slug: str, version: Optional[str] = None):
        version = version or self.env.get("MC_VERSION")
        self._rate_limit()
        res = self.client.get(f"/project/{slug}/version")
        if res.status_code != 200:
            raise RuntimeError(f"Failed to fetch versions for {slug}: {res.status_code}")
        versions = res.json()
        for v in versions:
            if isinstance(v, dict):
                if version in v.get("game_versions", []) and self.env.get("MC_LOADER") in v.get("loaders", []):
                  # pkg = McPkgConig()
                  ## in this plugin we create the pkg to return

                  return v
        raise RuntimeError(f"No matching version found for {slug} with version {version} and loader {self.env.get('MC_LOADER')}")

    def do_fetch(self, slug: str, version: Optional[str] = None):
        mod_version = self.do_search(slug, version)
        file = next((f for f in mod_version["files"] if f.get("primary", True)), None)
        if not file:
            raise RuntimeError(f"No downloadable file found for {slug}")

        file_path = self._download_file(file["url"], file["filename"])
        return file_path

    def _download_file(self, url: str, filename: str) -> Path:
        target_dir = Path(self.env.repo_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / filename

        if target_path.exists():
            mcpkg_logger.info(f"[modrith] Using cached mod: {target_path}")
            return target_path

        self._rate_limit()
        try:
            with httpx.stream("GET", url, headers={"User-Agent": USER_AGENT}) as response:
                response.raise_for_status()
                with target_path.open("wb") as f:
                    for chunk in response.iter_bytes():
                        f.write(chunk)
            mcpkg_logger.info(f"[modrith] Downloaded mod to: {target_path}")
            return target_path
        except Exception as e:
            error_handler(f"Failed to download {url}", e)

    def do_parse(self, node: dict):
        """
        Handle node from the YAML schema like:
        modrith:
          - fabric-api:
              version: "1.21.6"
        """
        if isinstance(node, str):
            return {"slug": node, "version": None}
        elif isinstance(node, dict):
            for k, v in node.items():
                return {"slug": k, "version": v.get("version")}
        else:
            raise ValueError(f"Invalid mod node: {node}")

    def do_package(self, slug: str, version: Optional[str] = None):
        mod_version = self.do_search(slug, version)
        file = next((f for f in mod_version["files"] if f.get("primary", True)), None)
        if not file:
            raise RuntimeError(f"No downloadable file for {slug}")

        file_path = self._download_file(file["url"], file["filename"])
        file_sha512 = cache.sha512sum(file_path)
        file_sha1 = cache.sha1sum(file_path)

        pkg_entry = {
            "name": slug,
            "sha": file_sha512,
            "loader": self.env.get("MC_LOADER"),
            "provider": "modrith",
            "source": file["url"],
            "version": mod_version["version_number"],
            "file_name": file["filename"],
            "timestamp": int(time.time()),
            "signed_by": f"{self.env.server}_packagegroup.json.sig",
            "dependencies": mod_version.get("dependencies", [])
        }

        return pkg_entry
