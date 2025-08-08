from abc import ABC, abstractmethod

class McPkgApi(ABC):
    @abstractmethod
    def base_url(self) -> str:
        """Return the base URL of the API provider (e.g., https://api.modrinth.com)."""
        pass

    @abstractmethod
    def name(self) -> str:
        """Return a unique short name for the provider (e.g., 'modrith', 'curse_forge')."""
        pass

    def key(self) -> str | None:
        """Return an API key if required. Can return None by default."""
        return None

    @abstractmethod
    def do_parse(self, node: dict) -> dict:
        """
        Parse the mcpkg YAML node for this provider.
        Returns a normalized internal dict for resolution/download.
        """
        pass

    @abstractmethod
    def do_fetch(self, parsed: dict, server_name: str, modloader: str, mc_version: str) -> dict:
        """
        Download and return metadata about the mod.
        Should return a dict with at least:
        - name
        - file_name
        - source
        - sha
        - version
        - loader
        - timestamp
        - provider
        """
        pass

    @abstractmethod
    def do_package(self, downloaded_metadata: list[dict], output_dir: str, group_name: str) -> tuple[str, str]:
        """
        Bundle metadata and mods into:
        - A zipped mod group
        - A JSON package group file

        Returns:
        - Path to the .zip file
        - Path to the .json metadata file
        """
        pass

    @abstractmethod
    def do_search(self, mod_name: str, version: str = None) -> list[dict]:
        """
        Search for mods by name (and optionally by MC version).
        Returns a list of results (with slug, version, title, summary, etc).
        """
        pass
