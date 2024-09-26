from contextlib import asynccontextmanager

from fastapi import FastAPI

from app_infra.app_logger import make_logger
from app_infra.cache import make_cache
from db import make_db, clean_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    make_logger()
    await make_db()
    await make_cache()
    yield
    await clean_db()


def add_lifespan(app: FastAPI):
    app.router.lifespan_context = lifespan
