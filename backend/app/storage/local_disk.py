"""Local disk storage provider for content-addressable evidence files."""

import hashlib
from pathlib import Path

from app.core.config import settings
from app.storage.base import StorageProvider


class LocalDiskStorage(StorageProvider):
    """Stores files on the local filesystem named by their SHA-256 hash.

    Used for local development, automated tests, and offline demos.
    """

    def __init__(self, base_dir: str | None = None):
        # Set up the local directory where files will be saved
        self.base_dir = Path(base_dir or settings.local_storage_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def store(self, content: bytes, content_type: str = "application/json") -> tuple[str, str]:
        """Save content to disk under a filename matching its SHA-256 hash."""
        content_hash = hashlib.sha256(content).hexdigest()
        file_path = self.base_dir / content_hash

        if not file_path.exists():
            file_path.write_bytes(content)

        storage_uri = f"file://{file_path.resolve().as_posix()}"
        return content_hash, storage_uri

    def retrieve(self, storage_uri: str) -> bytes | None:
        """Read content bytes from local disk using the file URI."""
        if storage_uri.startswith("file://"):
            path_str = storage_uri[len("file://"):]
            file_path = Path(path_str)
        else:
            file_path = Path(storage_uri)

        if not file_path.exists():
            return None

        return file_path.read_bytes()

    def exists(self, content_hash: str) -> bool:
        """Check if a file with the given content hash exists in the local directory."""
        file_path = self.base_dir / content_hash
        return file_path.exists()
