from datetime import datetime, timezone
from fastapi import FastAPI
from typing import Optional
from uuid import UUID
from maleo.dtos.config.middleware import MiddlewareConfig
from maleo.dtos.contexts.operation import generate_operation_context
from maleo.dtos.contexts.service import ServiceContext
from maleo.dtos.key.rsa import Complete
from maleo.enums.operation import (
    Layer,
    Origin,
    Target,
    SystemOperationType,
)
from maleo.logging.enums import Level
from maleo.logging.logger import Middleware
from maleo.mixins.timestamp import OperationTimestamp
from maleo.schemas.operation.system import (
    SystemOperationAction,
    SuccessfulSystemOperation,
)
from maleo.schemas.response import NoDataResponse
from maleo.utils.name import get_fully_qualified_name
from .authentication import add_authentication_middleware
from .base import add_base_middleware
from .cors import add_cors_middleware
from .rate_limit import RateLimiter
from .response_builder import ResponseBuilder
from .state import add_state_middleware


class MiddlewareManager:
    """MiddlewareManager class"""

    key = "middleware_manager"
    name = "MiddlewareManager"

    def __init__(
        self,
        app: FastAPI,
        *,
        operation_id: UUID,
        configuration: MiddlewareConfig,
        keys: Complete,
        logger: Middleware,
        service_context: Optional[ServiceContext] = None,
    ):
        self._app = app
        self._configuration = configuration
        self._keys = keys
        self._logger = logger

        self._service_context = (
            service_context
            if service_context is not None
            else ServiceContext.from_env()
        )

        operation_context = generate_operation_context(
            origin=Origin.SERVICE,
            layer=Layer.UTILITY,
            layer_details={
                "component": {"key": self.key, "name": self.name},
            },
            target=Target.INTERNAL,
            target_details={"fully_qualified_name": get_fully_qualified_name()},
        )

        operation_action = SystemOperationAction(
            type=SystemOperationType.INITIALIZATION,
            details={
                "type": "manager_initialization",
                "manager_key": self.key,
                "manager_name": self.name,
            },
        )

        executed_at = datetime.now(tz=timezone.utc)

        self.rate_limiter = RateLimiter(
            operation_id=operation_id,
            configuration=self._configuration.rate_limiter,
            logger=self._logger,
            service_context=self._service_context,
        )

        self._response_builder = ResponseBuilder(
            logger=self._logger,
            private_key=self._keys.private_rsa_key,
            service_context=self._service_context,
            operation_id=operation_id,
        )

        SuccessfulSystemOperation[None, NoDataResponse[None]](
            service_context=self._service_context,
            id=operation_id,
            context=operation_context,
            timestamp=OperationTimestamp.completed_now(executed_at),
            summary=f"Successfully initialized {self.name}",
            request_context=None,
            authentication=None,
            action=operation_action,
            response=NoDataResponse[None](metadata=None, other=None),
        ).log(logger=self._logger, level=Level.INFO)

    def add(self, operation_id: UUID):
        operation_context = generate_operation_context(
            origin=Origin.SERVICE,
            layer=Layer.UTILITY,
            layer_details={
                "component": {"key": self.key, "name": self.name},
            },
            target=Target.INTERNAL,
            target_details={"fully_qualified_name": get_fully_qualified_name()},
        )

        operation_action = SystemOperationAction(
            type=SystemOperationType.STARTUP,
            details={"type": "middlewares_addition"},
        )

        executed_at = datetime.now(tz=timezone.utc)

        add_base_middleware(
            self._app,
            logger=self._logger,
            private_key=self._keys.private_rsa_key,
            rate_limiter=self.rate_limiter,
            response_builder=self._response_builder,
            service_context=self._service_context,
            operation_id=operation_id,
        )
        add_state_middleware(
            self._app,
            logger=self._logger,
            service_context=self._service_context,
            operation_id=operation_id,
        )
        add_authentication_middleware(self._app, public_key=self._keys.public_rsa_key)
        add_cors_middleware(self._app, configuration=self._configuration.cors)

        SuccessfulSystemOperation[None, NoDataResponse[None]](
            service_context=self._service_context,
            id=operation_id,
            context=operation_context,
            timestamp=OperationTimestamp.completed_now(executed_at),
            summary="Successfully added all middlewares to FastAPI application",
            request_context=None,
            authentication=None,
            action=operation_action,
            response=NoDataResponse[None](metadata=None, other=None),
        ).log(logger=self._logger, level=Level.INFO)
