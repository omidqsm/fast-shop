from fastapi import FastAPI

from router.auth import router as auth_router
from router.product import router as product_router
from router.address import router as address_router


def add_routers(app: FastAPI):
    app.include_router(auth_router)
    app.include_router(product_router)
    app.include_router(address_router)
