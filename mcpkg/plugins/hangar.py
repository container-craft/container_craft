import time
import json
import zipfile
import httpx

from pathlib import Path
from typing import Optional, List

from mcpkg.plugins.api import McPkgApi
from container_craft_core.logger import get_logger
from container_craft_core.error_handler import error_handler
from container_craft_core.config import context
from container_craft_core.cache import cache

log = get_logger("mcpkg.plugins.hanger")


class HangerClient(McPkgApi):
    def name(self) -> str:
        return "hanger"

    def base_url(self) -> str:
        return "https://cdn.hangar.papermc.io"

    def key(self) -> Optional[str]:
        return None

    def do_parse(self, node: dict) -> dict:
        if isinstance(node, str) and node.startswith("http"):
            return {"url": node}
        raise ValueError(f"[hanger] Invalid config node: {node}")

    def do_fetch(self, parsed: dict, server_name: str, modloader: str, mc_version: str) -> dict:
        url = parsed["url"]
        file_name = url.split("/")[-1]
        repo_dir = Path(context.env["MC_REPO_DIR"])
        repo_dir.mkdir(parents=True, exist_ok=True)

        file_path = repo_dir / file_name

        if not file_path.exists():
            log.info(f"[hanger] Downloading: {url}")
            try:
                with httpx.stream("GET", url) as response:
                    response.raise_for_status()
                    with open(file_path, "wb") as f:
                        for chunk in response.iter_bytes():
                            f.write(chunk)
            except Exception as e:
                error_handler(f"[hanger] Failed to download {url}", e)
        else:
            log.info(f"[hanger] Using cached file: {file_name}")

        sha = cache.sha512sum(file_path)

        return {
            "name": file_name.rsplit(".", 1)[0],
            "version": "unknown",
            "sha": sha,
            "file_name": file_name,
            "source": url,
            "loader": modloader,
            "provider": "hanger",
            "timestamp": int(time.time()),
            "signed_by": f"{server_name}_packagegroup.json.sig"
        }

    def do_package(self, downloaded_metadata: List[dict], output_dir: str, group_name: str) -> tuple[str, str]:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 1. ZIP all JARs
        zip_path = output_path / f"{group_name}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for meta in downloaded_metadata:
                jar_path = output_path / meta["file_name"]
                if not jar_path.exists():
                    raise FileNotFoundError(f"Missing mod jar: {jar_path}")
                zipf.write(jar_path, arcname=meta["file_name"])
        log.info(f"[hanger] Created ZIP archive: {zip_path}")

        # 2. Write packagegroup metadata
        json_path = output_path / f"{group_name}_packagegroup.json"
        with open(json_path, "w") as f:
            json.dump(downloaded_metadata, f, indent=2)
        log.info(f"[hanger] Created packagegroup JSON: {json_path}")

        # 3. Write .mcpkg pointer
        mcpkg_path = output_path / f"{group_name}.mcpkg"
        repo_url = context.env["MC_REPO_URL"]
        with open(mcpkg_path, "w") as f:
            f.write(f"{repo_url}/{group_name}_packagegroup.json\n")
        log.info(f"[hanger] Wrote .mcpkg: {mcpkg_path}")

        return str(zip_path), str(json_path)
