import json
import traceback
from Crypto.PublicKey.RSA import RsaKey
from datetime import datetime, timezone
from fastapi import FastAPI, Request, status
from fastapi.responses import Response, JSONResponse
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.types import ASGIApp
from typing import Optional
from uuid import uuid4
from maleo.constants.error import STATUS_CODE_ERROR_TYPE_MAP
from maleo.dtos.authentication import OptionalAuthentication
from maleo.dtos.contexts.operation import generate_operation_context
from maleo.dtos.contexts.service import ServiceContext
from maleo.dtos.contexts.request import RequestContext
from maleo.dtos.contexts.response import ResponseContext
from maleo.dtos.error import Error
from maleo.enums.error import ErrorType
from maleo.enums.operation import (
    OperationType,
    SystemOperationType,
    Origin,
    Layer,
    Target,
)
from maleo.exceptions import TooManyRequests, InternalServerError
from maleo.logging.enums import Level
from maleo.logging.logger import Middleware
from maleo.mixins.timestamp import OperationTimestamp
from maleo.schemas.operation.request import (
    FailedRequestOperation,
    SuccessfulRequestOperation,
)
from maleo.schemas.operation.resource import (
    extract_resource_operation_action,
)
from maleo.schemas.operation.system import (
    SystemOperationAction,
    SuccessfulSystemOperation,
)
from maleo.schemas.response import (
    ErrorResponse,
    InternalServerErrorResponse,
    SuccessResponse,
    NoDataResponse,
)
from maleo.types.base.uuid import OptionalUUID
from maleo.utils.extractor import ResponseBodyExtractor
from maleo.utils.name import get_fully_qualified_name
from .rate_limit import RateLimiter
from .response_builder import ResponseBuilder


class BaseMiddleware(BaseHTTPMiddleware):
    """Base Middleware for Maleo"""

    key = "base_middleware"
    name = "Base Middleware"

    def __init__(
        self,
        app: ASGIApp,
        logger: Middleware,
        private_key: RsaKey,
        rate_limiter: RateLimiter,
        response_builder: ResponseBuilder,
        service_context: Optional[ServiceContext] = None,
        operation_id: OptionalUUID = None,
    ) -> None:
        super().__init__(app, None)
        self._logger = logger
        self._private_key = private_key

        self._service_context = (
            service_context
            if service_context is not None
            else ServiceContext.from_env()
        )
        operation_id = operation_id if operation_id is not None else uuid4()

        self.rate_limiter = rate_limiter

        self._response_builder = response_builder

        operation_context = generate_operation_context(
            origin=Origin.SERVICE,
            layer=Layer.MIDDLEWARE,
            layer_details={
                "identifier": {
                    "key": self.key,
                    "name": self.name,
                }
            },
            target=Target.INTERNAL,
            target_details={"fully_qualified_name": get_fully_qualified_name()},
        )

        operation_action = SystemOperationAction(
            type=SystemOperationType.INITIALIZATION,
            details={
                "type": "class_initialization",
                "class_key": self.key,
                "class_name": self.name,
            },
        )

        SuccessfulSystemOperation[None, NoDataResponse[None]](
            service_context=self._service_context,
            id=operation_id,
            context=operation_context,
            timestamp=OperationTimestamp.now(),
            summary=f"Successfully initialized {self.name}",
            request_context=None,
            authentication=None,
            action=operation_action,
            response=NoDataResponse[None](metadata=None, other=None),
        ).log(logger=self._logger, level=Level.INFO)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Get all necessary states
        try:
            # Get Operation Id
            operation_id = request.state.operation_id

            # Get Request Context
            request_context = RequestContext.from_request(request=request)

            # Get Authentication
            authentication: OptionalAuthentication = (
                OptionalAuthentication.from_request(request=request)
            )

            # Get Operation action
            resource_operation_action = extract_resource_operation_action(
                request=request
            )

        except Exception as e:
            print("Unable to retrieve request's state:\n", traceback.format_exc())
            response = JSONResponse(
                content=InternalServerErrorResponse(
                    other={
                        "exc_type": type(e).__name__,
                        "exc_data": {
                            "message": str(e),
                            "args": e.args,
                        },
                    }
                ).model_dump(),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
            return response

        operation_context = generate_operation_context(
            origin=Origin.SERVICE,
            layer=Layer.MIDDLEWARE,
            layer_details={"type": "base"},
            target=Target.INTERNAL,
            target_details={"fully_qualified_name": get_fully_qualified_name()},
        )

        executed_at = datetime.now(tz=timezone.utc)
        error = None

        try:
            user_id = (
                authentication.credentials.token.payload.u_i
                if authentication.credentials.token is not None
                else None
            )
            organization_id = (
                authentication.credentials.token.payload.o_i
                if authentication.credentials.token is not None
                else None
            )
            is_rate_limited = await self.rate_limiter.is_rate_limited(
                ip_address=request_context.ip_address,
                user_id=user_id,
                organization_id=organization_id,
            )
            if is_rate_limited:
                raise TooManyRequests[OptionalAuthentication](
                    OperationType.REQUEST,
                    service_context=self._service_context,
                    operation_id=operation_id,
                    operation_context=operation_context,
                    operation_timestamp=OperationTimestamp.completed_now(executed_at),
                    operation_summary="Too many requests",
                    request_context=request_context,
                    authentication=authentication,
                    operation_action=resource_operation_action,
                )

            response = await call_next(request)

            operation_timestamp = OperationTimestamp.completed_now(executed_at)

            final_response = self._response_builder.add_headers(
                operation_id=operation_id,
                request_context=request_context,
                authentication=authentication,
                response=response,
                responded_at=operation_timestamp.completed_at,
                process_time=operation_timestamp.duration,
            )

            if (
                response.media_type
                and "application/json" in response.media_type.lower()
            ):
                response_body, final_response = (
                    await ResponseBodyExtractor.async_extract(response)
                )
                response_context = ResponseContext(
                    status_code=final_response.status_code,
                    media_type=final_response.media_type,
                    headers=final_response.headers.items(),
                    body=response_body,
                )

                # Try to parse JSON dict
                try:
                    json_dict = json.loads(response_body)
                except Exception:
                    print("Failed loading response's json:\n", traceback.format_exc())
                    json_dict = None  # not valid JSON, leave as None

                if json_dict is not None:
                    try:
                        if 200 <= response.status_code < 400:
                            operation = SuccessfulRequestOperation[
                                OptionalAuthentication,
                                type(resource_operation_action),
                                SuccessResponse,
                            ](
                                service_context=self._service_context,
                                id=operation_id,
                                context=operation_context,
                                timestamp=operation_timestamp,
                                summary="Successfully processed request",
                                action=resource_operation_action,
                                request_context=request_context,
                                authentication=authentication,
                                response_context=response_context,
                                response=SuccessResponse.model_validate(json_dict),
                            )
                            operation.log(self._logger, Level.INFO)
                        elif 400 <= response.status_code <= 500:
                            validated_response = ErrorResponse.model_validate(json_dict)
                            error = Error(
                                type=STATUS_CODE_ERROR_TYPE_MAP.get(
                                    response.status_code,
                                    ErrorType.INTERNAL_SERVER_ERROR,
                                ),
                                status_code=response.status_code,
                                code=validated_response.code,
                                message=validated_response.message,
                                description=validated_response.description,
                                details=validated_response.other,
                                traceback=None,
                            )
                            operation = FailedRequestOperation[
                                Error,
                                OptionalAuthentication,
                                type(resource_operation_action),
                                ErrorResponse,
                            ](
                                service_context=self._service_context,
                                id=operation_id,
                                context=operation_context,
                                timestamp=operation_timestamp,
                                summary="Failed processing request",
                                error=error,
                                action=resource_operation_action,
                                request_context=request_context,
                                authentication=authentication,
                                response_context=response_context,
                                response=validated_response,
                            )
                            operation.log(self._logger, Level.ERROR)
                    except Exception:
                        print(
                            "Failed generating request operation from response:\n",
                            traceback.format_exc(),
                        )
            return final_response
        except TooManyRequests[OptionalAuthentication] as tmr:
            response = JSONResponse(
                content=tmr.response.model_dump(mode="json"),
                status_code=tmr.error_spec.status_code,
            )

            operation = tmr.generate_operation(OperationType.REQUEST)

            final_response = self._response_builder.add_headers(
                operation_id=operation_id,
                request_context=request_context,
                authentication=authentication,
                response=response,
                responded_at=operation.timestamp.completed_at,
                process_time=operation.timestamp.duration,
            )

            response_body, final_response = await ResponseBodyExtractor.async_extract(
                response
            )
            response_context = ResponseContext(
                status_code=final_response.status_code,
                media_type=final_response.media_type,
                headers=final_response.headers.items(),
                body=response_body,
            )
            operation.response_context = response_context
            operation.log(logger=self._logger, level=Level.ERROR)

            return final_response
        except Exception as e:
            print("Failed processing request:\n", traceback.format_exc())
            operation_timestamp = OperationTimestamp.completed_now(executed_at)

            error = InternalServerError(
                OperationType.REQUEST,
                service_context=self._service_context,
                operation_id=operation_id,
                operation_context=operation_context,
                operation_timestamp=operation_timestamp,
                operation_summary="Unexpected error occured while processing request",
                operation_action=resource_operation_action,
                request_context=request_context,
                authentication=authentication,
                details={
                    "exc_type": type(e).__name__,
                    "exc_data": {
                        "message": str(e),
                        "args": e.args,
                    },
                },
            )

            response = JSONResponse(
                content=error.response.model_dump(mode="json"),
                status_code=error.error_spec.status_code,
            )

            final_response = self._response_builder.add_headers(
                operation_id=operation_id,
                request_context=request_context,
                authentication=authentication,
                response=response,
                responded_at=operation_timestamp.completed_at,
                process_time=operation_timestamp.duration,
            )

            response_body, final_response = await ResponseBodyExtractor.async_extract(
                final_response
            )
            response_context = ResponseContext(
                status_code=final_response.status_code,
                media_type=final_response.media_type,
                headers=final_response.headers.items(),
                body=response_body,
            )

            operation = error.generate_operation(OperationType.REQUEST)
            operation.response_context = response_context
            operation.log(logger=self._logger, level=Level.ERROR)

            return final_response


def add_base_middleware(
    app: FastAPI,
    *,
    logger: Middleware,
    private_key: RsaKey,
    rate_limiter: RateLimiter,
    response_builder: ResponseBuilder,
    service_context: Optional[ServiceContext] = None,
    operation_id: OptionalUUID = None,
) -> None:
    """
    Add Base middleware to the FastAPI application.

    Args:
        app:FastAPI application instance
        keys:RSA keys for signing and token generation
        logger:Middleware logger instance
        maleo_soma:Client manager for soma services
        allow_origins:CORS allowed origins
        allow_methods:CORS allowed methods
        allow_headers:CORS allowed headers
        allow_credentials:CORS allow credentials flag
        limit:Request count limit per window
        window:Time window for rate limiting (seconds)
        cleanup_interval:Cleanup interval for old IP data (seconds)
        ip_timeout:IP timeout after last activity (seconds)

    Example:
        ```python
        add_base_middleware(
            app=app,
            keys=rsa_keys,
            logger=middleware_logger,
            maleo_soma=client_manager,
            limit=10,
            window=1,
            cleanup_interval=60,
            ip_timeout=300
        )
        ```
    """
    app.add_middleware(
        BaseMiddleware,
        logger=logger,
        private_key=private_key,
        rate_limiter=rate_limiter,
        response_builder=response_builder,
        service_context=service_context,
        operation_id=operation_id,
    )
