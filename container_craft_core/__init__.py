LOCAL_VERSION = "0.1"

SUPPORTED_VERSIONS = {
    "0.1",
}

def is_supported(version: str) -> bool:
    return version in SUPPORTED_VERSIONS
