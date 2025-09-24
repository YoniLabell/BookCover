from __future__ import annotations

import redis
from rq import Connection, Worker

from ..core.config import get_settings


def run_worker() -> None:
    settings = get_settings()
    connection = redis.from_url(settings.redis_url)
    with Connection(connection):
        worker = Worker(["bookready"])
        worker.work()


if __name__ == "__main__":
    run_worker()
