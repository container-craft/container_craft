import os
import time
import httpx
from typing import List, Optional, Dict, Any

from mcpkg.api import McPkgApi
from container_craft_core import log
from container_craft_core.config import context
from container_craft_core.cache import verify_hash, compute_sha512

class CurseForgeClient(McPkgApi):
    def __init__(self):
        super().__init__()
        self.logger = log.getLogger("mcpkg.plugins.curseforge")

        self.api_key = context.env.get("CURSE_FORGE_KEY")
        if not self.api_key:
            raise RuntimeError("CURSE_FORGE_KEY must be set in environment or config.")

        self.client = httpx.Client(
            base_url="https://api.curseforge.com",
            headers={
                "Accept": "application/json",
                "x-api-key": self.api_key,
                "User-Agent": "mcpkg/0.1 (https://github.com/YOUR_USERNAME/container_craft)"
            },
            timeout=10.0
        )

    def search(self, mod_name: str) -> List[Dict[str, Any]]:
        self.logger.info(f"Searching for mod '{mod_name}' on CurseForge...")

        params = {
            "gameId": 432,        # Minecraft
            "searchFilter": mod_name,
            "pageSize": 10,
            "classId": 6          # Mods
        }

        response = self.client.get("/v1/mods/search", params=params)
        response.raise_for_status()
        data = response.json()

        results = data.get("data", [])
        for mod in results:
            self.logger.debug(f"Found: {mod['name']} (ID: {mod['id']})")

        return results

    def resolve(self, mod_id: str, version: Optional[str] = None) -> Dict[str, Any]:
        self.logger.info(f"Resolving mod ID '{mod_id}' (version={version})...")

        mod_resp = self.client.get(f"/v1/mods/{mod_id}")
        mod_resp.raise_for_status()
        mod_info = mod_resp.json()["data"]

        files_resp = self.client.get(f"/v1/mods/{mod_id}/files")
        files_resp.raise_for_status()
        files = files_resp.json()["data"]

        file_info = None
        if version:
            for f in files:
                if f["displayName"].startswith(version) or version in f["displayName"]:
                    file_info = f
                    break
        else:
            file_info = files[0] if files else None

        if not file_info:
            raise RuntimeError(f"No version found matching '{version}'")

        return {
            "mod": mod_info,
            "file": file_info
        }

    def do_package(self, mod_id: str, version: Optional[str] = None) -> str:
        info = self.resolve(mod_id, version)
        mod, file = info["mod"], info["file"]

        file_id = file["id"]
        file_name = file["fileName"]
        download_url_resp = self.client.get(f"/v1/mods/files/{file_id}/download-url")
        download_url_resp.raise_for_status()
        download_url = download_url_resp.json()["data"]

        self.logger.info(f"Downloading: {download_url}")
        download_path = os.path.join(context.env["MC_DOWNLOADS_DIR"], file_name)

        with self.client.stream("GET", download_url) as r:
            r.raise_for_status()
            with open(download_path, "wb") as f:
                for chunk in r.iter_bytes():
                    f.write(chunk)

        sha = compute_sha512(download_path)
        verify_hash(download_path, sha)

        out_path = os.path.join(context.env["MC_CACHE_DIR"], f"{mod['slug']}.mcpkg")
        metadata = {
            "name": mod["name"],
            "version": file["displayName"],
            "file_name": file_name,
            "sha": sha,
            "loader": self._guess_loader(file),
            "provider": "curseforge",
            "source": download_url,
            "timestamp": int(time.time()),
            "signed_by": None
        }

        self._write_package_metadata(out_path, metadata)
        self.logger.info(f"Wrote .mcpkg: {out_path}")
        return out_path

    def _guess_loader(self, file_info: Dict[str, Any]) -> str:
        # Heuristic based on filename or file metadata
        name = file_info["fileName"].lower()
        if "fabric" in name:
            return "fabric"
        if "forge" in name:
            return "forge"
        if "neoforge" in name:
            return "neoforge"
        if "quilt" in name:
            return "quilt"
        return "unknown"

    def _write_package_metadata(self, path: str, metadata: Dict[str, Any]) -> None:
        import yaml
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            yaml.safe_dump(metadata, f)
