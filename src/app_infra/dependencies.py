from aredis_om import get_redis_connection

from config import settings
from db import async_session_maker


async def get_db_session():
    async with async_session_maker() as session:
        yield session


async def get_redis():
    redis_conn = get_redis_connection(url=settings.redis_url, decode_responses=True)
    try:
        yield redis_conn
    finally:
        await redis_conn.close()
