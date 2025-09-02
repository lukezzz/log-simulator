from typing import Annotated, AsyncGenerator

from fastapi import Depends
from redis import asyncio as aioredis

from core.settings import cfg


def register_redis(redis_url):
    return aioredis.from_url(redis_url, decode_responses=True)


async def get_auth_redis() -> AsyncGenerator[aioredis.Redis, None]:
    rds = register_redis(str(cfg.REDIS_URI))
    try:
        yield rds
    finally:
        await rds.close()


async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
    rds = register_redis(str(cfg.REDIS_URI))
    try:
        yield rds
    finally:
        await rds.close()


authRedisSession = Annotated[aioredis.Redis, Depends(get_auth_redis)]
redisSession = Annotated[aioredis.Redis, Depends(get_redis)]
