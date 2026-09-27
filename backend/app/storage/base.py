from abc import ABC, abstractmethod


class StorageProvider(ABC):
    """Abstract interface for content-addressable evidence storage."""

    @abstractmethod
    def store(self, content: bytes, content_type: str = "application/json") -> tuple[str, str]:
        """
        Store binary or serialized content.

        Returns:
            tuple[str, str]: (content_hash, storage_uri)
        """
        pass

    @abstractmethod
    def retrieve(self, storage_uri: str) -> bytes | None:
        """Retrieve stored content by its URI."""
        pass

    @abstractmethod
    def exists(self, content_hash: str) -> bool:
        """Check if an object with the given content hash exists."""
        pass
