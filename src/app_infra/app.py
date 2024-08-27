from fastapi import FastAPI

from app_infra.exceptions_handler import add_exception_handlers
from app_infra.lifespan import add_lifespan
from app_infra.middlewares import add_middlewares
from router import add_routers


def make_app(app: FastAPI) -> FastAPI:
    add_routers(app)
    add_middlewares(app)
    add_exception_handlers(app)
    add_lifespan(app)
    return app
