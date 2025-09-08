from contextlib import (
    AbstractAsyncContextManager,
    AbstractContextManager,
    asynccontextmanager,
    contextmanager,
)
from datetime import datetime, timezone
from pydantic import ValidationError
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker, Session
from typing import (
    AsyncGenerator,
    Generator,
    Generic,
    Literal,
    Optional,
    Tuple,
    Union,
    overload,
)
from uuid import uuid4
from maleo.dtos.authentication import GenericAuthentication
from maleo.dtos.contexts.operation import generate_operation_context
from maleo.dtos.contexts.request import RequestContext
from maleo.dtos.contexts.service import ServiceContext
from maleo.enums.operation import (
    OperationType,
    SystemOperationType,
    Origin,
    Layer,
    Target,
)
from maleo.exceptions import (
    MaleoException,
    UnprocessableEntity,
    DatabaseError,
    InternalServerError,
)
from maleo.mixins.timestamp import OperationTimestamp
from maleo.schemas.operation.system import (
    SystemOperationAction,
    SuccessfulSystemOperation,
)
from maleo.schemas.response import NoDataResponse
from maleo.types.base.uuid import OptionalUUID
from maleo.logging.enums import Level
from maleo.logging.logger import Database
from ..enums import Connection
from ..config import SQLConfigT


class SessionManager(Generic[SQLConfigT]):
    def __init__(
        self,
        config: SQLConfigT,
        engines: Tuple[AsyncEngine, Engine],
        logger: Database,
        service_context: Optional[ServiceContext] = None,
    ):
        self._config = config
        self._async_engine, self._sync_engine = engines
        self._logger = logger
        self._service_context = (
            service_context
            if service_context is not None
            else ServiceContext.from_env()
        )
        self._operation_context = generate_operation_context(
            origin=Origin.SERVICE,
            layer=Layer.UTILITY,
            target=Target.DATABASE,
            target_details=self._config.model_dump(),
        )

        self._async_sessionmaker: async_sessionmaker[AsyncSession] = async_sessionmaker[
            AsyncSession
        ](bind=self._async_engine, expire_on_commit=True)
        self._sync_sessionmaker: sessionmaker[Session] = sessionmaker[Session](
            bind=self._sync_engine, expire_on_commit=True
        )

    async def _async_session_handler(
        self,
        operation_id: OptionalUUID = None,
        request_context: Optional[RequestContext] = None,
        authentication: Optional[GenericAuthentication] = None,
    ) -> AsyncGenerator[AsyncSession, None]:
        """Reusable function for managing async database session."""
        operation_id = operation_id if operation_id is not None else uuid4()
        operation_action = SystemOperationAction(
            type=SystemOperationType.DATABASE_CONNECTION, details=None
        )
        session = self._async_sessionmaker()
        SuccessfulSystemOperation[
            Optional[GenericAuthentication], NoDataResponse[None]
        ](
            service_context=self._service_context,
            id=operation_id,
            context=self._operation_context,
            timestamp=OperationTimestamp.now(),
            summary="Successfully created new async database session",
            request_context=request_context,
            authentication=authentication,
            action=operation_action,
            response=NoDataResponse[None](metadata=None, other=None),
        ).log(
            self._logger, level=Level.DEBUG
        )

        executed_at = datetime.now(tz=timezone.utc)
        try:
            yield session  # Provide session
            await session.commit()  # Auto-commit on success
            SuccessfulSystemOperation[
                Optional[GenericAuthentication], NoDataResponse[None]
            ](
                service_context=self._service_context,
                id=operation_id,
                context=self._operation_context,
                timestamp=OperationTimestamp.completed_now(executed_at),
                summary="Successfully committed async database transaction",
                request_context=request_context,
                authentication=authentication,
                action=operation_action,
                response=NoDataResponse[None](metadata=None, other=None),
            ).log(
                self._logger, level=Level.INFO
            )
        except SQLAlchemyError as se:
            await session.rollback()  # Rollback on error
            error = DatabaseError[Optional[GenericAuthentication]](
                OperationType.SYSTEM,
                service_context=self._service_context,
                operation_id=operation_id,
                operation_context=self._operation_context,
                operation_timestamp=OperationTimestamp.completed_now(executed_at),
                operation_summary="SQLAlchemy error occured while handling async database session",
                request_context=request_context,
                authentication=authentication,
                operation_action=operation_action,
                details={
                    "exc_type": type(se).__name__,
                    "exc_data": {
                        "message": str(se),
                        "args": se.args,
                    },
                },
            )
            operation = error.generate_operation(OperationType.SYSTEM)
            operation.log(self._logger, level=Level.ERROR)
            raise error from se
        except ValidationError as ve:
            await session.rollback()  # Rollback on error
            error = UnprocessableEntity[Optional[GenericAuthentication]](
                OperationType.SYSTEM,
                service_context=self._service_context,
                operation_id=operation_id,
                operation_context=self._operation_context,
                operation_timestamp=OperationTimestamp.completed_now(executed_at),
                operation_summary="Validation error occured while handling async database session",
                request_context=request_context,
                authentication=authentication,
                operation_action=operation_action,
                details=ve.errors(),
            )
            operation = error.generate_operation(OperationType.SYSTEM)
            operation.log(self._logger, level=Level.ERROR)
            raise error from ve
        except MaleoException:
            raise
        except Exception as e:
            await session.rollback()  # Rollback on error
            error = InternalServerError[Optional[GenericAuthentication]](
                OperationType.SYSTEM,
                service_context=self._service_context,
                operation_id=operation_id,
                operation_context=self._operation_context,
                operation_timestamp=OperationTimestamp.completed_now(executed_at),
                operation_summary="Unexpected error occured while handling async database session",
                request_context=request_context,
                authentication=authentication,
                operation_action=operation_action,
                details={
                    "exc_type": type(e).__name__,
                    "exc_data": {
                        "message": str(e),
                        "args": e.args,
                    },
                },
            )
            operation = error.generate_operation(OperationType.SYSTEM)
            operation.log(self._logger, level=Level.ERROR)
            raise error from e
        finally:
            await session.close()  # Ensure session closes
            SuccessfulSystemOperation[
                Optional[GenericAuthentication], NoDataResponse[None]
            ](
                service_context=self._service_context,
                id=operation_id,
                context=self._operation_context,
                timestamp=OperationTimestamp.now(),
                summary="Successfully closed async database session",
                request_context=request_context,
                authentication=authentication,
                action=operation_action,
                response=NoDataResponse[None](metadata=None, other=None),
            ).log(
                self._logger, level=Level.INFO
            )

    def _sync_session_handler(
        self,
        operation_id: OptionalUUID = None,
        request_context: Optional[RequestContext] = None,
        authentication: Optional[GenericAuthentication] = None,
    ) -> Generator[Session, None, None]:
        """Reusable function for managing sync database session."""
        operation_id = operation_id if operation_id is not None else uuid4()
        operation_action = SystemOperationAction(
            type=SystemOperationType.DATABASE_CONNECTION, details=None
        )
        session = self._sync_sessionmaker()
        SuccessfulSystemOperation[
            Optional[GenericAuthentication], NoDataResponse[None]
        ](
            service_context=self._service_context,
            id=operation_id,
            context=self._operation_context,
            timestamp=OperationTimestamp.now(),
            summary="Successfully created new sync database session",
            request_context=request_context,
            authentication=authentication,
            action=operation_action,
            response=NoDataResponse[None](metadata=None, other=None),
        ).log(
            self._logger, level=Level.DEBUG
        )

        executed_at = datetime.now(tz=timezone.utc)
        try:
            yield session  # Provide session
            session.commit()  # Auto-commit on success
            SuccessfulSystemOperation[
                Optional[GenericAuthentication], NoDataResponse[None]
            ](
                service_context=self._service_context,
                id=operation_id,
                context=self._operation_context,
                timestamp=OperationTimestamp.completed_now(executed_at),
                summary="Successfully committed sync database transaction",
                request_context=request_context,
                authentication=authentication,
                action=operation_action,
                response=NoDataResponse[None](metadata=None, other=None),
            ).log(
                self._logger, level=Level.INFO
            )
        except SQLAlchemyError as se:
            session.rollback()  # Rollback on error
            error = DatabaseError[Optional[GenericAuthentication]](
                OperationType.SYSTEM,
                service_context=self._service_context,
                operation_id=operation_id,
                operation_context=self._operation_context,
                operation_timestamp=OperationTimestamp.completed_now(executed_at),
                operation_summary="SQLAlchemy error occured while handling sync database session",
                request_context=request_context,
                authentication=authentication,
                operation_action=operation_action,
                details={
                    "exc_type": type(se).__name__,
                    "exc_data": {
                        "message": str(se),
                        "args": se.args,
                    },
                },
            )
            operation = error.generate_operation(OperationType.SYSTEM)
            operation.log(self._logger, level=Level.ERROR)
            raise error from se
        except ValidationError as ve:
            session.rollback()  # Rollback on error
            error = UnprocessableEntity[Optional[GenericAuthentication]](
                OperationType.SYSTEM,
                service_context=self._service_context,
                operation_id=operation_id,
                operation_context=self._operation_context,
                operation_timestamp=OperationTimestamp.completed_now(executed_at),
                operation_summary="Validation error occured while handling sync database session",
                request_context=request_context,
                authentication=authentication,
                operation_action=operation_action,
                details=ve.errors(),
            )
            operation = error.generate_operation(OperationType.SYSTEM)
            operation.log(self._logger, level=Level.ERROR)
            raise error from ve
        except MaleoException:
            raise
        except Exception as e:
            session.rollback()  # Rollback on error
            error = InternalServerError[Optional[GenericAuthentication]](
                OperationType.SYSTEM,
                service_context=self._service_context,
                operation_id=operation_id,
                operation_context=self._operation_context,
                operation_timestamp=OperationTimestamp.completed_now(executed_at),
                operation_summary="Unexpected error occured while handling sync database session",
                request_context=request_context,
                authentication=authentication,
                operation_action=operation_action,
                details={
                    "exc_type": type(e).__name__,
                    "exc_data": {
                        "message": str(e),
                        "args": e.args,
                    },
                },
            )
            operation = error.generate_operation(OperationType.SYSTEM)
            operation.log(self._logger, level=Level.ERROR)
            raise error from e
        finally:
            session.close()  # Ensure session closes
            SuccessfulSystemOperation[
                Optional[GenericAuthentication], NoDataResponse[None]
            ](
                service_context=self._service_context,
                id=operation_id,
                context=self._operation_context,
                timestamp=OperationTimestamp.now(),
                summary="Successfully closed sync database session",
                request_context=request_context,
                authentication=authentication,
                action=operation_action,
                response=NoDataResponse[None](metadata=None, other=None),
            ).log(
                self._logger, level=Level.INFO
            )

    @asynccontextmanager
    async def _async_context_manager(
        self,
        operation_id: OptionalUUID = None,
        request_context: Optional[RequestContext] = None,
        authentication: Optional[GenericAuthentication] = None,
    ) -> AsyncGenerator[AsyncSession, None]:
        """Async context manager implementation."""
        async for session in self._async_session_handler(
            operation_id,
            request_context,
            authentication,
        ):
            yield session

    @contextmanager
    def _sync_context_manager(
        self,
        operation_id: OptionalUUID = None,
        request_context: Optional[RequestContext] = None,
        authentication: Optional[GenericAuthentication] = None,
    ) -> Generator[Session, None, None]:
        """Sync context manager implementation."""
        yield from self._sync_session_handler(
            operation_id,
            request_context,
            authentication,
        )

    # Overloaded context manager methods
    @overload
    def get(
        self,
        connection: Literal[Connection.ASYNC],
        operation_id: OptionalUUID = None,
        request_context: Optional[RequestContext] = None,
        authentication: Optional[GenericAuthentication] = None,
    ) -> AbstractAsyncContextManager[AsyncSession]: ...

    @overload
    def get(
        self,
        connection: Literal[Connection.SYNC],
        operation_id: OptionalUUID = None,
        request_context: Optional[RequestContext] = None,
        authentication: Optional[GenericAuthentication] = None,
    ) -> AbstractContextManager[Session]: ...

    def get(
        self,
        connection: Connection = Connection.ASYNC,
        operation_id: OptionalUUID = None,
        request_context: Optional[RequestContext] = None,
        authentication: Optional[GenericAuthentication] = None,
    ) -> Union[
        AbstractAsyncContextManager[AsyncSession], AbstractContextManager[Session]
    ]:
        """Context manager for manual session handling."""
        if operation_id is None:
            operation_id = uuid4()
        if connection is Connection.ASYNC:
            return self._async_context_manager(
                operation_id,
                request_context,
                authentication,
            )
        else:
            return self._sync_context_manager(
                operation_id,
                request_context,
                authentication,
            )

    # Alternative: More explicit methods
    @asynccontextmanager
    async def get_async(
        self,
        operation_id: OptionalUUID = None,
        request_context: Optional[RequestContext] = None,
        authentication: Optional[GenericAuthentication] = None,
    ) -> AsyncGenerator[AsyncSession, None]:
        """Explicit async context manager."""
        async for session in self._async_session_handler(
            operation_id,
            request_context,
            authentication,
        ):
            yield session

    @contextmanager
    def get_sync(
        self,
        operation_id: OptionalUUID = None,
        request_context: Optional[RequestContext] = None,
        authentication: Optional[GenericAuthentication] = None,
    ) -> Generator[Session, None, None]:
        """Explicit sync context manager."""
        yield from self._sync_session_handler(
            operation_id,
            request_context,
            authentication,
        )

    def as_async_dependency(
        self,
        operation_id: OptionalUUID = None,
        request_context: Optional[RequestContext] = None,
        authentication: Optional[GenericAuthentication] = None,
    ):
        """Explicit async dependency injection."""

        def dependency() -> AsyncGenerator[AsyncSession, None]:
            return self._async_session_handler(
                operation_id,
                request_context,
                authentication,
            )

        return dependency

    def as_sync_dependency(
        self,
        operation_id: OptionalUUID = None,
        request_context: Optional[RequestContext] = None,
        authentication: Optional[GenericAuthentication] = None,
    ):
        """Explicit sync dependency injection."""

        def dependency() -> Generator[Session, None, None]:
            return self._sync_session_handler(
                operation_id,
                request_context,
                authentication,
            )

        return dependency

    def dispose(self):
        self._sync_sessionmaker.close_all()
