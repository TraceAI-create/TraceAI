import hashlib
from pathlib import Path

from app.core.config import settings
from app.storage.base import StorageProvider


class LocalDiskStorage(StorageProvider):
    """
    Local filesystem content-addressable storage.
    Used for local development, tests, and offline demo.
    """

    def __init__(self, base_dir: str | None = None):
        self.base_dir = Path(base_dir or settings.local_storage_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def store(self, content: bytes, content_type: str = "application/json") -> tuple[str, str]:
        content_hash = hashlib.sha256(content).hexdigest()
        file_path = self.base_dir / content_hash

        if not file_path.exists():
            file_path.write_bytes(content)

        storage_uri = f"file://{file_path.resolve().as_posix()}"
        return content_hash, storage_uri

    def retrieve(self, storage_uri: str) -> bytes | None:
        if storage_uri.startswith("file://"):
            path_str = storage_uri[len("file://"):]
            file_path = Path(path_str)
        else:
            file_path = Path(storage_uri)

        if not file_path.exists():
            return None

        return file_path.read_bytes()

    def exists(self, content_hash: str) -> bool:
        file_path = self.base_dir / content_hash
        return file_path.exists()
