"""Utility helpers for uploading content to MinIO."""

import io
import uuid

from minio import Minio

from ..config import settings


def get_minio_client() -> Minio:
    return Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
    )


def upload_text(content: str, prefix: str = "reports", content_type: str = "text/markdown") -> str:
    client = get_minio_client()
    bucket = settings.minio_bucket
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)

    object_name = f"{prefix.rstrip('/')}/{uuid.uuid4().hex}.md"
    body = content.encode("utf-8")
    client.put_object(
        bucket,
        object_name,
        io.BytesIO(body),
        length=len(body),
        content_type=content_type,
    )

    if settings.minio_public_url:
        return f"{settings.minio_public_url.rstrip('/')}/{bucket}/{object_name}"
    protocol = "https" if settings.minio_secure else "http"
    return f"{protocol}://{settings.minio_endpoint}/{bucket}/{object_name}"
