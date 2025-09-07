import traceback
from datetime import datetime, timezone
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp
from typing import Optional
from uuid import uuid4, UUID
from maleo.dtos.contexts.operation import generate_operation_context
from maleo.dtos.contexts.service import ServiceContext
from maleo.enums.operation import (
    Layer,
    Origin,
    Target,
    SystemOperationType,
)
from maleo.schemas.operation.resource import extract_resource_operation_action
from maleo.schemas.operation.system import (
    SystemOperationAction,
    SuccessfulSystemOperation,
)
from maleo.schemas.response import InternalServerErrorResponse, NoDataResponse
from maleo.logging.enums import Level
from maleo.logging.logger import Middleware
from maleo.mixins.timestamp import OperationTimestamp
from maleo.types.base.uuid import OptionalUUID
from maleo.utils.name import get_fully_qualified_name


class StateMiddleware(BaseHTTPMiddleware):
    """Middleware for all request's state management"""

    key = "state_middleware"
    name = "StateMiddleware"

    def __init__(
        self,
        app: ASGIApp,
        logger: Middleware,
        service_context: Optional[ServiceContext] = None,
        operation_id: OptionalUUID = None,
    ) -> None:
        super().__init__(app, None)
        self._logger = logger
        self._service_context = (
            service_context
            if service_context is not None
            else ServiceContext.from_env()
        )
        operation_id = operation_id if operation_id is not None else uuid4()

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
        try:
            # Assign Operation Id
            operation_id = request.headers.get("x-operation-id", None)
            if operation_id is None:
                operation_id = uuid4()
            else:
                operation_id = UUID(operation_id)
            request.state.operation_id = operation_id

            # Assign Operation action
            resource_operation_action = extract_resource_operation_action(
                request, False
            )
            request.state.resource_operation_action = resource_operation_action

            # Assign Request Id
            request.state.request_id = uuid4()

            # Assign Requested at
            request.state.requested_at = datetime.now(tz=timezone.utc)

            # Call and return response
            return await call_next(request)
        except Exception as e:
            print(
                "Unexpected error while assigning request state:\n",
                traceback.format_exc(),
            )
            return JSONResponse(
                content=InternalServerErrorResponse(
                    message="Unexpected error while assigning request state",
                    other={
                        "exc_type": type(e).__name__,
                        "exc_data": {
                            "message": str(e),
                            "args": e.args,
                        },
                    },
                ).model_dump(mode="json"),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


def add_state_middleware(
    app: FastAPI,
    *,
    logger: Middleware,
    service_context: Optional[ServiceContext] = None,
    operation_id: OptionalUUID = None,
) -> None:
    app.add_middleware(
        StateMiddleware,
        logger=logger,
        service_context=service_context,
        operation_id=operation_id,
    )
