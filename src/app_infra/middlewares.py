import uuid

from fastapi import FastAPI, Request

from app_infra.app_logger import get_logger

logger = get_logger()


def add_middlewares(app: FastAPI):

    @app.middleware('http')
    async def add_request_id(request: Request, call_next):
        request.state.request_id = str(uuid.uuid4())
        response = await call_next(request)
        return response
