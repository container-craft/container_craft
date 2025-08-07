import json
import jsonschema
import yaml
from pathlib import Path
from container_craft_core.logger import get_logger
from container_craft_core.error_handler import error_handler
from container_craft_core.env import ContainerCraftEnv
from container_craft_core.__version__ import LOCAL_VERSION, SUPPORTED_VERSIONS

logger = get_logger(__name__)


class SchemaValidator:
    def __init__(self, schema_path: str = None, env: ContainerCraftEnv = None):
        """
        Initializes the SchemaValidator with a schema file path.
        If no path is provided, it tries to infer from the MC_CONFIG location.
        """
        self.env = env or ContainerCraftEnv()
        self.schema_path = self._resolve_schema_path(schema_path)
        self.schema = None
        self._load_schema()

    def _resolve_schema_path(self, schema_path: str = None) -> Path:
        if schema_path:
            return Path(schema_path).resolve()

        # Try to find a schema next to MC_CONFIG
        mc_config = Path(self.env.get("MC_CONFIG"))
        default_dir = mc_config.parent

        candidates = [
            default_dir / "container_craft_schema.json",
            default_dir / "container_craft_schema.yml",
        ]

        for candidate in candidates:
            if candidate.exists():
                logger.debug(f"Found schema file: {candidate}")
                return candidate.resolve()

        # Fallback to internal bundled schema
        internal = Path(__file__).parent / "lint" / "container_craft_schema.json"
        if internal.exists():
            logger.debug(f"Falling back to internal schema: {internal}")
            return internal.resolve()

        error_handler.handle_error(
            f"No schema found in {default_dir} or internal fallback. "
            f"Tried: {candidates + [internal]}"
        )

    def _load_schema(self):
        try:
            content = self.schema_path.read_text()
            if self.schema_path.suffix in {".yaml", ".yml"}:
                self.schema = yaml.safe_load(content)
            else:
                self.schema = json.loads(content)
        except Exception as e:
            error_handler.handle_error(f"Failed to load schema: {self.schema_path}", e)

    def validate(self, data: dict):
        """
        Validates the given data against the loaded JSON Schema.
        Raises ValueError on failure.
        """
        if self.schema is None:
            self._load_schema()

        # Check for required version key
        config_version = data.get("version")
        if not config_version:
            raise ValueError("Missing required 'version' field in configuration.")

        if config_version not in SUPPORTED_VERSIONS:
            raise ValueError(
                f"Unsupported config version '{config_version}'. "
                f"Supported versions: {', '.join(SUPPORTED_VERSIONS)}. "
                f"Current tool version: {LOCAL_VERSION}"
            )

        try:
            jsonschema.validate(instance=data, schema=self.schema)
        except jsonschema.ValidationError as e:
            raise ValueError(f"Schema validation error: {e.message}")
