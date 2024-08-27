import time
from typing import Callable

from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from fastapi import Request, Response

from app_infra.app_logger import get_logger
from config import settings

logger = get_logger()


class LogRoute(APIRoute):
    # todo: get_request_body should move to somewhere else and await request.body() should be replace with cheaper code
    #       maybe moving it to helper layer in RequestHelper class would be a good idea
    @staticmethod
    async def get_request_body(request: Request) -> dict | None:
        if settings.auth_route_prefix not in request.url.path:
            request_body = await request.json() if await request.body() else None
            return request_body

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        # this acts as like the last added middleware (innermost layer of onion!)
        async def custom_route_handler(request: Request) -> Response:

            log_data = {
                'url': str(request.url),
                'request_id': request.state.request_id,
                'request_body': await self.get_request_body(request)
            }
            start_time = time.time()
            try:
                response = await original_route_handler(request)

            # todo: why am i catching exceptions here?! specially when it's only for logging. it must go to exception
            #       layer in app_infra
            except RequestValidationError as e:
                logger.exception(str(e.args[0][0]['msg']), request_id=request.state.request_id)
                raise e
            except Exception as e:
                logger.exception(str(e), request_id=request.state.request_id)
                # re-raise the exception to catch in defined exception handlers (if we return a response, exception
                # handler won't catch the exception
                raise e
            process_time = time.time() - start_time
            log_data['process_time'] = process_time
            log_data['status_code'] = response.status_code
            log_data['response_body'] = response.body.decode()
            logger.info('request log', **log_data)
            return response

        return custom_route_handler
