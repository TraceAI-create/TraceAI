"""Base interface for content-addressable evidence storage providers."""

from abc import ABC, abstractmethod


class StorageProvider(ABC):
    """Abstract interface for storing and retrieving evidence files by content hash."""

    @abstractmethod
    def store(self, content: bytes, content_type: str = "application/json") -> tuple[str, str]:
        """Store binary or text content.

        Returns:
            A tuple of (content_hash, storage_uri).
        """
        pass

    @abstractmethod
    def retrieve(self, storage_uri: str) -> bytes | None:
        """Retrieve stored content bytes using its storage URI."""
        pass

    @abstractmethod
    def exists(self, content_hash: str) -> bool:
        """Check whether content with the given hash already exists in storage."""
        pass
