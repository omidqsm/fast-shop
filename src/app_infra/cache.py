from aredis_om import get_redis_connection, Migrator

from config import settings
from model.cache import ProductCache


async def make_cache():
    redis_conn = get_redis_connection(url=settings.redis_url, decode_responses=True)
    ProductCache.Meta.database = redis_conn
    await Migrator().run()
    await redis_conn.close()
