import time
import json
import httpx
import zipfile

from pathlib import Path
from typing import Optional, List, Dict

from mcpkg.api import McPkgApi
from container_craft_core.logger import get_logger
from container_craft_core.config import context
from container_craft_core.cache import sha512sum
from container_craft_core.error_handler import handle_error

logger = get_logger("mcpkg.plugins.curse_forge")


class CurseForgeClient(McPkgApi):
    def __init__(self):
        self.api_key = context.env.get("CURSE_FORGE_KEY")
        if not self.api_key:
            raise RuntimeError("CURSE_FORGE_KEY must be set in environment or config.")

        self.client = httpx.Client(
            base_url="https://api.curseforge.com",
            headers={
                "Accept": "application/json",
                "x-api-key": self.api_key,
                "User-Agent": "mcpkg/0.1 (https://github.com/container-craft/container_craft)"
            },
            timeout=10.0
        )

    def name(self) -> str:
        return "curse_forge"

    def base_url(self) -> str:
        return "https://api.curseforge.com"

    def key(self) -> Optional[str]:
        return self.api_key

    def do_parse(self, node: dict) -> dict:
        if isinstance(node, str):
            return {"slug": node, "version": None}
        elif isinstance(node, dict):
            for k, v in node.items():
                return {"slug": k, "version": v.get("version")}
        raise ValueError(f"[curse_forge] Invalid mod node: {node}")

    def do_search(self, mod_name: str, version: Optional[str] = None) -> List[dict]:
        logger.info(f"[curse_forge] Searching: {mod_name}")
        params = {
            "gameId": 432,
            "searchFilter": mod_name,
            "classId": 6,
            "pageSize": 10
        }
        resp = self.client.get("/v1/mods/search", params=params)
        resp.raise_for_status()
        return resp.json().get("data", [])

    def do_fetch(self, parsed: dict, server_name: str, modloader: str, mc_version: str) -> dict:
        slug = parsed["slug"]
        target_dir = Path(context.env["MC_REPO_DIR"])
        target_dir.mkdir(parents=True, exist_ok=True)

        mod_id = self._resolve_mod_id(slug)
        if not mod_id:
            raise RuntimeError(f"[curse_forge] Failed to resolve slug: {slug}")

        mod_info = self._get_mod_info(mod_id)
        file_info = self._select_file(mod_id, modloader, mc_version, parsed.get("version"))

        file_id = file_info["id"]
        file_name = file_info["fileName"]

        resp = self.client.get(f"/v1/mods/files/{file_id}/download-url")
        resp.raise_for_status()
        download_url = resp.json()["data"]

        file_path = target_dir / file_name
        if not file_path.exists():
            logger.info(f"[curse_forge] Downloading {file_name}")
            try:
                with httpx.stream("GET", download_url) as response:
                    response.raise_for_status()
                    with open(file_path, "wb") as f:
                        for chunk in response.iter_bytes():
                            f.write(chunk)
            except Exception as e:
                handle_error(f"[curse_forge] Failed to download {download_url}", e)
        else:
            logger.info(f"[curse_forge] Cached: {file_name}")

        sha = sha512sum(file_path)

        return {
            "name": mod_info["name"],
            "version": file_info["displayName"],
            "file_name": file_name,
            "sha": sha,
            "loader": context.env.get("MC_LOADER", "unknown"),
            "provider": "curse_forge",
            "source": download_url,
            "timestamp": int(time.time()),
            "signed_by": f"{server_name}_packagegroup.json.sig",
            "authors": [a["name"] for a in mod_info.get("authors", [])]
        }

    def do_package(self, downloaded_metadata: List[dict], output_dir: str, group_name: str) -> tuple[str, str]:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        zip_path = output_path / f"{group_name}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for meta in downloaded_metadata:
                jar_path = output_path / meta["file_name"]
                if not jar_path.exists():
                    raise FileNotFoundError(f"[curse_forge] Missing mod jar: {jar_path}")
                zipf.write(jar_path, arcname=meta["file_name"])
        logger.info(f"[curse_forge] Wrote ZIP: {zip_path}")

        json_path = output_path / f"{group_name}_packagegroup.json"
        with open(json_path, "w") as f:
            json.dump(downloaded_metadata, f, indent=2)
        logger.info(f"[curse_forge] Wrote metadata: {json_path}")

        mcpkg_path = output_path / f"{group_name}.mcpkg"
        repo_url = context.env["MC_REPO_URL"]
        with open(mcpkg_path, "w") as f:
            f.write(f"{repo_url}/{group_name}_packagegroup.json\n")
        logger.info(f"[curse_forge] Wrote .mcpkg: {mcpkg_path}")

        return str(zip_path), str(json_path)

    def _resolve_mod_id(self, slug: str) -> Optional[int]:
        results = self.do_search(slug)
        return results[0]["id"] if results else None

    def _get_mod_info(self, mod_id: int) -> dict:
        resp = self.client.get(f"/v1/mods/{mod_id}")
        resp.raise_for_status()
        return resp.json()["data"]

    def _select_file(self, mod_id: int, loader: str, version: Optional[str], override: Optional[str] = None) -> dict:
        resp = self.client.get(f"/v1/mods/{mod_id}/files")
        resp.raise_for_status()
        files = resp.json()["data"]

        for f in files:
            if version and version not in f.get("gameVersions", []):
                continue
            if loader and loader.lower() not in [v.lower() for v in f.get("gameVersions", [])]:
                continue
            return f

        if files:
            return files[0]
        raise RuntimeError(f"[curse_forge] No file found for mod {mod_id}")
