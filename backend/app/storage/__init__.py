"""Storage provider factory for content-addressable evidence files."""

from app.core.config import settings
from app.storage.base import StorageProvider
from app.storage.local_disk import LocalDiskStorage
from app.storage.supabase_storage import SupabaseStorage

# Singleton storage provider instance
_storage_singleton: StorageProvider | None = None


def get_storage_provider() -> StorageProvider:
    """Return the active storage provider instance.

    Uses SupabaseStorage if Supabase credentials are configured,
    otherwise defaults to LocalDiskStorage.
    """
    global _storage_singleton
    if _storage_singleton is None:
        if settings.supabase_url and settings.supabase_key:
            _storage_singleton = SupabaseStorage()
        else:
            _storage_singleton = LocalDiskStorage()
    return _storage_singleton
