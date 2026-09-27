import hashlib
import tempfile
from app.storage.local_disk import LocalDiskStorage


def test_local_storage_store_and_retrieve():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = LocalDiskStorage(base_dir=tmpdir)
        payload = b"content to be hashed and stored in traceai evidence store"
        expected_hash = hashlib.sha256(payload).hexdigest()

        content_hash, uri = storage.store(payload)
        assert content_hash == expected_hash
        assert storage.exists(content_hash) is True

        retrieved = storage.retrieve(uri)
        assert retrieved == payload


def test_storage_content_addressable_deduplication():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = LocalDiskStorage(base_dir=tmpdir)
        payload = b"identical duplicate document"
        h1, u1 = storage.store(payload)
        h2, u2 = storage.store(payload)

        assert h1 == h2
        assert u1 == u2
