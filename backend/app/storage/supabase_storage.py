import hashlib
import httpx

from app.core.config import settings
from app.storage.base import StorageProvider
from app.storage.local_disk import LocalDiskStorage


class SupabaseStorage(StorageProvider):
    """
    Supabase Storage provider for content-addressable evidence.
    Falls back cleanly to LocalDiskStorage if Supabase credentials are not supplied.
    """

    def __init__(
        self,
        supabase_url: str | None = None,
        supabase_key: str | None = None,
        bucket: str | None = None,
    ):
        self.supabase_url = (supabase_url or settings.supabase_url or "").rstrip("/")
        self.supabase_key = supabase_key or settings.supabase_key or ""
        self.bucket = bucket or settings.supabase_storage_bucket
        self.fallback = LocalDiskStorage()

    @property
    def is_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_key)

    def store(self, content: bytes, content_type: str = "application/json") -> tuple[str, str]:
        content_hash = hashlib.sha256(content).hexdigest()

        if not self.is_configured:
            return self.fallback.store(content, content_type=content_type)

        endpoint = f"{self.supabase_url}/storage/v1/object/{self.bucket}/{content_hash}"
        headers = {
            "Authorization": f"Bearer {self.supabase_key}",
            "apikey": self.supabase_key,
            "Content-Type": content_type,
            "x-upsert": "true",
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                res = client.post(endpoint, headers=headers, content=content)
                if res.status_code in (200, 201):
                    storage_uri = f"supabase://{self.bucket}/{content_hash}"
                    return content_hash, storage_uri
        except Exception:
            pass

        # Fallback to local storage if network or credentials fail
        return self.fallback.store(content, content_type=content_type)

    def retrieve(self, storage_uri: str) -> bytes | None:
        if storage_uri.startswith("file://") or not self.is_configured:
            return self.fallback.retrieve(storage_uri)

        if storage_uri.startswith("supabase://"):
            parts = storage_uri[len("supabase://"):].split("/", 1)
            bucket = parts[0] if len(parts) > 1 else self.bucket
            key = parts[1] if len(parts) > 1 else parts[0]

            endpoint = f"{self.supabase_url}/storage/v1/object/authenticated/{bucket}/{key}"
            headers = {
                "Authorization": f"Bearer {self.supabase_key}",
                "apikey": self.supabase_key,
            }

            try:
                with httpx.Client(timeout=15.0) as client:
                    res = client.get(endpoint, headers=headers)
                    if res.status_code == 200:
                        return res.content
            except Exception:
                pass

        return self.fallback.retrieve(storage_uri)

    def exists(self, content_hash: str) -> bool:
        if not self.is_configured:
            return self.fallback.exists(content_hash)
        return self.fallback.exists(content_hash)
