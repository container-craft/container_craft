LOCAL_VERSION = "0.1"

SUPPORTED_VERSIONS = {
    "0.1",
}

def is_supported(version: str) -> bool:
    return version in SUPPORTED_VERSIONS

from .logger import get_logger, logger, core_logger, mcpkg_logger 
from .error_handler import error_handler

from .env import env
from .config.context import context
from .config.schema_validator import SchemaValidator
from .cache import cache
