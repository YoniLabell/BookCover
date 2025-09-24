from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any, Dict

import boto3

from ..core.config import get_settings


@dataclass
class PresignedPost:
    url: str
    fields: Dict[str, Any]
    key: str


class StorageService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._client = boto3.client(
            "s3",
            endpoint_url=self.settings.s3_endpoint,
            aws_access_key_id=self.settings.s3_access_key,
            aws_secret_access_key=self.settings.s3_secret_key,
            region_name=self.settings.s3_region,
        )

    def generate_key(self, project_id: str, kind: str, filename: str) -> str:
        suffix = filename.split("/")[-1]
        unique = uuid.uuid4().hex
        return f"projects/{project_id}/{kind}/{unique}-{suffix}"

    def presign_post(self, key: str, content_type: str, content_length: int) -> PresignedPost:
        conditions = [
            {"bucket": self.settings.s3_bucket},
            ["starts-with", "$key", key.rsplit("/", 1)[0] + "/"],
            ["content-length-range", 1, content_length],
        ]
        response = self._client.generate_presigned_post(
            Bucket=self.settings.s3_bucket,
            Key=key,
            Fields={"Content-Type": content_type},
            Conditions=conditions,
            ExpiresIn=self.settings.s3_presign_expiry,
        )
        fields = response.get("fields", {})
        fields.setdefault("Content-Type", content_type)
        return PresignedPost(url=response["url"], fields=fields, key=key)

    def object_url(self, key: str) -> str:
        return f"{self.settings.s3_endpoint}/{self.settings.s3_bucket}/{key}"
