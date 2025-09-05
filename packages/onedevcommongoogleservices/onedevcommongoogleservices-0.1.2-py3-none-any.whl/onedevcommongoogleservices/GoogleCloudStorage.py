from __future__ import annotations
import io
import os
from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

from google.cloud.storage import Client, Bucket, Blob
from google.api_core.retry import Retry

# importa sua classe de auth
from onedevcommongoogleservices.GoogleServicesAuth import GoogleServicesAuth

BytesLike = Union[bytes, bytearray, memoryview]


@dataclass
class UploadResult:
    bucket: str
    name: str
    public_url: str
    self_link: Optional[str] = None
    size: Optional[int] = None
    content_type: Optional[str] = None
    generation: Optional[str] = None
    crc32c: Optional[str] = None
    md5_hash: Optional[str] = None


class GoogleCloudStorageService:
    """
    Google Cloud Storage usando a MESMA credencial do GoogleServicesAuth.

    - Construtor recebe `auth: GoogleServicesAuth` e (opcional) `default_bucket`.
    - Requer escopo GCS apropriado no `GoogleServicesAuth` (ex.: devstorage.read_write).
    """

    # escopos mínimos recomendados (use o que você quiser checar)
    _RECOMMENDED_SCOPES = {
        "https://www.googleapis.com/auth/devstorage.read_write",
        "https://www.googleapis.com/auth/devstorage.full_control",
        "https://www.googleapis.com/auth/devstorage.read_only",
    }

    def __init__(
        self,
        auth: "GoogleServicesAuth",
        *,
        default_bucket: Optional[str] = None,
        project_id: Optional[str] = None,
        require_scope_check: bool = False,
    ) -> None:
        self._auth = auth
        if require_scope_check:
            self._ensure_storage_scope()

        self._client: Client = self._auth.storage(project_id=project_id)
        self._default_bucket = default_bucket

    def _ensure_storage_scope(self) -> None:
        scopes = set(self._auth.scopes)
        if not scopes.intersection(self._RECOMMENDED_SCOPES):
            raise RuntimeError(
                "Scopes de Storage ausentes no GoogleServicesAuth. "
                "Inclua pelo menos 'https://www.googleapis.com/auth/devstorage.read_write' "
                "ou '.../devstorage.full_control' ao instanciar o GoogleServicesAuth."
            )

    def _bucket(self, bucket_name: Optional[str]) -> Bucket:
        name = bucket_name or self._default_bucket
        if not name:
            raise ValueError("Bucket não informado (nem default_bucket configurado).")
        return self._client.bucket(name)

    def _blob(self, bucket_name: Optional[str], blob_name: str) -> Blob:
        return self._bucket(bucket_name).blob(blob_name)

    def ensure_bucket(self, bucket_name: str, *, location: Optional[str] = None, storage_class: str = "STANDARD") -> Bucket:
        bucket = self._client.lookup_bucket(bucket_name)
        if bucket:
            return bucket
        bucket = self._client.bucket(bucket_name)
        if location:
            bucket.location = location
        bucket.storage_class = storage_class
        return self._client.create_bucket(bucket)

    def upload_file(
        self,
        *,
        source_path: str,
        dest_blob: str,
        bucket_name: Optional[str] = None,
        content_type: Optional[str] = None,
        cache_control: Optional[str] = None,
        make_public: bool = False, 
        retry: Optional[Retry] = None,
        chunk_size: Optional[int] = None
    ) -> UploadResult:
        blob = self._blob(bucket_name, dest_blob)
        if cache_control:
            blob.cache_control = cache_control
        if chunk_size:
            blob.chunk_size = chunk_size  # p.ex. 8 * 1024 * 1024
        blob.upload_from_filename(source_path, content_type=content_type, retry=retry)
        if make_public:
            blob.make_public()
        return self._to_upload_result(blob)

    def upload_bytes(
        self,
        *,
        data: BytesLike,
        dest_blob: str,
        bucket_name: Optional[str] = None,
        content_type: Optional[str] = None,
        cache_control: Optional[str] = None,
        make_public: bool = False,
    ) -> UploadResult:
        blob = self._blob(bucket_name, dest_blob)
        if cache_control:
            blob.cache_control = cache_control
        blob.upload_from_string(data, content_type=content_type)
        if make_public:
            blob.make_public()
        return self._to_upload_result(blob)

    def upload_stream(
        self,
        *,
        stream: io.BufferedIOBase,
        dest_blob: str,
        bucket_name: Optional[str] = None,
        content_type: Optional[str] = None,
        cache_control: Optional[str] = None,
        make_public: bool = False,
        chunk_size: Optional[int] = None,
    ) -> UploadResult:
        blob = self._blob(bucket_name, dest_blob)
        if cache_control:
            blob.cache_control = cache_control
        if chunk_size:
            blob.chunk_size = chunk_size
        blob.upload_from_file(stream, content_type=content_type)
        if make_public:
            blob.make_public()
        return self._to_upload_result(blob)

    def download_to_file(
        self,
        *,
        blob_name: str,
        dest_path: str,
        bucket_name: Optional[str] = None,
    ) -> None:
        os.makedirs(os.path.dirname(dest_path) or ".", exist_ok=True)
        blob = self._blob(bucket_name, blob_name)
        blob.download_to_filename(dest_path)

    def download_as_bytes(
        self,
        *,
        blob_name: str,
        bucket_name: Optional[str] = None,
    ) -> bytes:
        blob = self._blob(bucket_name, blob_name)
        return blob.download_as_bytes()

    def download_as_stream(
        self,
        *,
        blob_name: str,
        bucket_name: Optional[str] = None,
        chunk_size: int = 1024 * 1024,
    ) -> Iterable[bytes]:
        blob = self._blob(bucket_name, blob_name)
        with blob.open("rb") as fh:
            while True:
                chunk = fh.read(chunk_size)
                if not chunk:
                    break
                yield chunk

    def file_exists(
        self, *, blob_name: str, bucket_name: Optional[str] = None
    ) -> bool:
        return self._blob(bucket_name, blob_name).exists()

    def get_metadata(
        self, *, blob_name: str, bucket_name: Optional[str] = None
    ) -> Dict[str, Any]:
        blob = self._blob(bucket_name, blob_name)
        blob.reload()
        return {
            "bucket": blob.bucket.name,
            "name": blob.name,
            "size": int(blob.size) if blob.size is not None else None,
            "content_type": blob.content_type,
            "updated": blob.updated.isoformat() if blob.updated else None,
            "crc32c": blob.crc32c,
            "md5_hash": blob.md5_hash,
            "storage_class": blob.storage_class,
            "kms_key_name": blob.kms_key_name,
            "generation": blob.generation,
            "metageneration": blob.metageneration,
            "cache_control": blob.cache_control,
        }

    def list_files(
        self,
        *,
        prefix: Optional[str] = None,
        recursive: bool = True,
        max_results: Optional[int] = None,
        bucket_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        bucket = self._bucket(bucket_name)
        iterator = bucket.list_blobs(
            prefix=prefix, 
            delimiter=None if recursive else "/", 
            max_results=max_results, 
        )
        files: List[Dict[str, Any]] = []
        for blob in iterator:
            files.append(
                {
                    "name": blob.name,
                    "size": int(blob.size) if blob.size is not None else None,
                    "updated": blob.updated.isoformat() if blob.updated else None,
                    "content_type": blob.content_type,
                    "crc32c": blob.crc32c,
                    "md5_hash": blob.md5_hash,
                }
            )
        return files

    def delete_file(
        self, *, blob_name: str, bucket_name: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        try:
            self._blob(bucket_name, blob_name).delete()
            return True, None
        except Exception as e:
            return False, str(e)

    def delete_prefix(
        self, *, prefix: str, bucket_name: Optional[str] = None
    ) -> Tuple[int, List[str]]:
        bucket = self._bucket(bucket_name)
        to_delete = list(bucket.list_blobs(prefix=prefix))
        failures: List[str] = []
        for b in to_delete:
            try:
                b.delete()
            except Exception:
                failures.append(b.name)
        return (len(to_delete) - len(failures), failures)

    def copy_file(
        self,
        *,
        src_blob: str,
        dest_blob: Optional[str] = None,
        src_bucket: Optional[str] = None,
        dest_bucket: Optional[str] = None,
    ) -> UploadResult:
        src_b = self._bucket(src_bucket)
        dst_b = self._bucket(dest_bucket)
        dest_name = dest_blob or src_blob
        new_blob = src_b.copy_blob(src_b.blob(src_blob), dst_b, dest_name)
        return self._to_upload_result(new_blob)

    def move_file(
        self,
        *,
        src_blob: str,
        dest_blob: Optional[str] = None,
        src_bucket: Optional[str] = None,
        dest_bucket: Optional[str] = None,
    ) -> UploadResult:
        result = self.copy_file(
            src_blob=src_blob,
            dest_blob=dest_blob,
            src_bucket=src_bucket,
            dest_bucket=dest_bucket,
        )
        self.delete_file(blob_name=src_blob, bucket_name=src_bucket)
        return result

    def get_signed_url(
        self,
        *,
        blob_name: str,
        expiration_seconds: int = 3600,
        method: str = "GET",
        content_type: Optional[str] = None,
        version: str = "v4",
        bucket_name: Optional[str] = None,
    ) -> str:
        blob = self._blob(bucket_name, blob_name)
        return blob.generate_signed_url(
            version=version,
            expiration=timedelta(seconds=expiration_seconds),
            method=method,
            content_type=content_type,
        )

    def _to_upload_result(self, blob: Blob) -> UploadResult:
        blob.reload()
        return UploadResult(
            bucket=blob.bucket.name,
            name=blob.name,
            public_url=blob.public_url,
            self_link=getattr(blob, "self_link", None),
            size=int(blob.size) if blob.size is not None else None,
            content_type=blob.content_type,
            generation=str(blob.generation) if blob.generation is not None else None,
            crc32c=blob.crc32c,
            md5_hash=blob.md5_hash,
        )
