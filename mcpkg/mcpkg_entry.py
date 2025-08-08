from dataclasses import dataclass, asdict
from typing import List, Dict, Any
import msgpack, zstandard as zstd

@dataclass
class McPkgEntry:
    name: str
    slug: str
    version: str
    loader: str
    mc_version: str
    file_name: str
    source: str
    sha512: str
    timestamp: str
    provider: str
    dependencies: List[Dict[str, Any]]

    def to_msgpack(self) -> bytes:
        return msgpack.packb(asdict(self), use_bin_type=True)

    @staticmethod
    def from_msgpack(b: bytes) -> "McPkgEntry":
        d = msgpack.unpackb(b, raw=False)
        return McPkgEntry(**d)

    def to_msgpack_zst(self) -> bytes:
        c = zstd.ZstdCompressor()
        return c.compress(self.to_msgpack())

    @staticmethod
    def from_msgpack_zst(b: bytes) -> "McPkgEntry":
        d = zstd.ZstdDecompressor().decompress(b)
        return McPkgEntry.from_msgpack(d)
