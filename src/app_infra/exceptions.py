import json
import traceback

from fastapi import HTTPException, FastAPI, Request
from fastapi.responses import JSONResponse

from app_infra.app_logger import get_logger

logger = get_logger()

# NOTE: these handlers also catch middleware exceptions


def add_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(HTTPException)
    def http_exception_handler(
            request: Request,
            exc: HTTPException
    ) -> JSONResponse:
        response = JSONResponse(
            content={
                'message': exc.detail,
                'request_id': request.state.request_id,
            },
            status_code=exc.status_code
        )
        return response

    @app.exception_handler(Exception)
    def http_exception_handler(
            request: Request,
            exc: HTTPException
    ) -> JSONResponse:
        response = JSONResponse(
            content={
                'message': 'unexpected internal error',
                'request_id': request.state.request_id,
            },
            status_code=500
        )
        return response
