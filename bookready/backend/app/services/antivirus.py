from __future__ import annotations

import socket
from typing import BinaryIO

import clamd

from ..core.config import get_settings


class AntivirusService:
    def __init__(self) -> None:
        settings = get_settings()
        self._client = clamd.ClamdNetworkSocket(host=settings.clamav_host, port=settings.clamav_port)

    def ping(self) -> bool:
        try:
            return self._client.ping().lower() == "pong"
        except (socket.error, clamd.ClamdError):
            return False

    def scan_stream(self, stream: BinaryIO) -> None:
        try:
            result = self._client.instream(stream)
        except (socket.error, clamd.ClamdError) as exc:
            raise RuntimeError("Unable to reach ClamAV daemon") from exc
        status, signature = result.get("stream", ("UNKNOWN", None))
        if status == "OK":
            return
        raise ValueError(f"Detected threat: {signature}")


def get_antivirus_service() -> AntivirusService:
    return AntivirusService()
