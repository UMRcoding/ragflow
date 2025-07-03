import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from util import format_timeout_duration, parse_timeout_duration

from core.container import init_containers, teardown_containers
from core.logger import logger

TIMEOUT = 10


@asynccontextmanager
async def _lifespan(app: FastAPI):
    """Asynchronous lifecycle management"""
    size = int(os.getenv("SANDBOX_EXECUTOR_MANAGER_POOL_SIZE", 1))

    success_count, total_task_count = await init_containers(size)
    logger.info(f"\n📊 Container pool initialization complete: {success_count}/{total_task_count} available")

    yield

    await teardown_containers()


def init():
    TIMEOUT = parse_timeout_duration(os.getenv("SANDBOX_TIMEOUT"))
    logger.info(f"Global timeout: {format_timeout_duration(TIMEOUT)}")
    return _lifespan
