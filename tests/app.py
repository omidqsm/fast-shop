import asyncio

from fastapi import FastAPI

from app_infra.app import make_app
from app_infra.cache import make_cache
from db import make_db


async def init():
    await make_db()
    make_cache()


asyncio.run(init())
pytest_app = FastAPI()
make_app(pytest_app)