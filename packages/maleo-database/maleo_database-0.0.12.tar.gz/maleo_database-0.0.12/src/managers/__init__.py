import traceback
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from elasticsearch import AsyncElasticsearch, Elasticsearch
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from redis.asyncio import Redis as AsyncRedis
from redis import Redis as SyncRedis
from sqlalchemy import MetaData, text
from typing import Generic, Optional, TypeVar
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
from maleo.exceptions import MaleoException, InternalServerError
from maleo.logging.enums import Level
from maleo.logging.logger import Database
from maleo.mixins.timestamp import OperationTimestamp
from maleo.schemas.operation.system import (
    SystemOperationAction,
    SuccessfulSystemOperation,
)
from maleo.schemas.response import NoDataResponse
from maleo.types.base.uuid import OptionalUUID
from ..config import (
    MySQLConfig,
    PostgreSQLConfig,
    SQLiteConfig,
    SQLServerConfig,
    SQLConfigT,
    ElasticsearchConfig,
    MongoDBConfig,
    RedisConfig,
    NoSQLConfigT,
    ConfigT,
)
from ..enums import Connection
from .client import (
    AsyncClientT,
    SyncClientT,
    ClientManager,
)
from .engine import EngineManager
from .session import SessionManager


class DatabaseManager(ABC, Generic[ConfigT]):
    def __init__(
        self,
        config: ConfigT,
        logger: Database,
        service_context: Optional[ServiceContext] = None,
    ) -> None:
        super().__init__()
        self._config = config
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
        )

    @abstractmethod
    async def async_check_connection(
        self,
        operation_id: OptionalUUID = None,
        request_context: Optional[RequestContext] = None,
        authentication: Optional[GenericAuthentication] = None,
    ) -> bool:
        pass

    @abstractmethod
    def sync_check_connection(
        self,
        operation_id: OptionalUUID = None,
        request_context: Optional[RequestContext] = None,
        authentication: Optional[GenericAuthentication] = None,
    ) -> bool:
        pass

    @abstractmethod
    async def dispose(self):
        pass


class SQLDatabaseManager(DatabaseManager[SQLConfigT], Generic[SQLConfigT]):
    def __init__(
        self,
        config: SQLConfigT,
        metadata: MetaData,
        logger: Database,
        service_context: Optional[ServiceContext] = None,
    ) -> None:
        super().__init__(config, logger, service_context)
        self._metadata = metadata
        self._operation_context.target.details = self._config.model_dump()
        self._engine_manager = EngineManager[SQLConfigT](config)
        self._session_manager = SessionManager(
            config=config,
            engines=self._engine_manager.get_all(),
            logger=self._logger,
            service_context=self._service_context,
        )
        self._metadata.create_all(bind=self._engine_manager.get(Connection.SYNC))

    @property
    def engine(self) -> EngineManager[SQLConfigT]:
        return self._engine_manager

    @property
    def session(self) -> SessionManager:
        return self._session_manager

    async def async_check_connnection(
        self,
        operation_id: OptionalUUID = None,
        request_context: Optional[RequestContext] = None,
        authentication: Optional[GenericAuthentication] = None,
    ) -> bool:
        """Check database connectivity by executing a simple query."""
        operation_id = operation_id if operation_id is not None else uuid4()
        operation_action = SystemOperationAction(
            type=SystemOperationType.DATABASE_CONNECTION, details=None
        )
        executed_at = datetime.now(tz=timezone.utc)
        try:
            async with self._session_manager.get(
                Connection.ASYNC,
                operation_id=operation_id,
                request_context=request_context,
                authentication=authentication,
            ) as session:
                await session.execute(text("SELECT 1"))
                SuccessfulSystemOperation[
                    Optional[GenericAuthentication], NoDataResponse[None]
                ](
                    service_context=self._service_context,
                    id=operation_id,
                    context=self._operation_context,
                    timestamp=OperationTimestamp.completed_now(executed_at),
                    summary="Database connectivity check successful",
                    request_context=request_context,
                    authentication=authentication,
                    action=operation_action,
                    response=NoDataResponse[None](metadata=None, other=None),
                ).log(
                    self._logger, Level.INFO
                )
            return True
        except MaleoException:
            return False
        except Exception as e:
            error = InternalServerError[Optional[GenericAuthentication]](
                OperationType.SYSTEM,
                service_context=self._service_context,
                operation_id=operation_id,
                operation_context=self._operation_context,
                operation_timestamp=OperationTimestamp.completed_now(executed_at),
                operation_summary="Unexpected error occured checking database connection",
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
            return False

    def sync_check_connection(
        self,
        operation_id: OptionalUUID = None,
        request_context: Optional[RequestContext] = None,
        authentication: Optional[GenericAuthentication] = None,
    ) -> bool:
        """Check database connectivity by executing a simple query."""
        operation_id = operation_id if operation_id is not None else uuid4()
        operation_action = SystemOperationAction(
            type=SystemOperationType.DATABASE_CONNECTION, details=None
        )
        executed_at = datetime.now(tz=timezone.utc)
        try:
            with self._session_manager.get(
                Connection.SYNC,
                operation_id=operation_id,
                request_context=request_context,
                authentication=authentication,
            ) as session:
                session.execute(text("SELECT 1"))
                SuccessfulSystemOperation[
                    Optional[GenericAuthentication], NoDataResponse[None]
                ](
                    service_context=self._service_context,
                    id=operation_id,
                    context=self._operation_context,
                    timestamp=OperationTimestamp.completed_now(executed_at),
                    summary="Database connectivity check successful",
                    request_context=request_context,
                    authentication=authentication,
                    action=operation_action,
                    response=NoDataResponse[None](metadata=None, other=None),
                ).log(
                    self._logger, Level.INFO
                )
            return True
        except MaleoException:
            return False
        except Exception as e:
            error = InternalServerError[Optional[GenericAuthentication]](
                OperationType.SYSTEM,
                service_context=self._service_context,
                operation_id=operation_id,
                operation_context=self._operation_context,
                operation_timestamp=OperationTimestamp.completed_now(executed_at),
                operation_summary="Unexpected error occured checking database connection",
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
            return False

    async def dispose(self):
        self._session_manager.dispose()
        await self._engine_manager.dispose()


class MySQLDatabaseManager(SQLDatabaseManager[MySQLConfig]):
    pass


class PostgreSQLDatabaseManager(SQLDatabaseManager[PostgreSQLConfig]):
    pass


class SQLiteDatabaseManager(SQLDatabaseManager[SQLiteConfig]):
    pass


class SQLServerDatabaseManager(SQLDatabaseManager[SQLServerConfig]):
    pass


SQLDatabaseManagerT = TypeVar(
    "SQLDatabaseManagerT",
    MySQLDatabaseManager,
    PostgreSQLDatabaseManager,
    SQLiteDatabaseManager,
    SQLServerDatabaseManager,
)


class NoSQLDatabaseManager(
    DatabaseManager[NoSQLConfigT],
    Generic[
        NoSQLConfigT,
        AsyncClientT,
        SyncClientT,
    ],
):
    def __init__(
        self,
        config: NoSQLConfigT,
        metadata: MetaData,
        logger: Database,
        service_context: Optional[ServiceContext] = None,
    ) -> None:
        super().__init__(config, logger, service_context)
        self._metadata = metadata
        self._operation_context.target.details = self._config.model_dump()
        self._client_manager = ClientManager[
            NoSQLConfigT,
            AsyncClientT,
            SyncClientT,
        ](config)

    @property
    def client(self) -> ClientManager[
        NoSQLConfigT,
        AsyncClientT,
        SyncClientT,
    ]:
        return self._client_manager

    async def async_check_connnection(
        self,
        operation_id: OptionalUUID = None,
        request_context: Optional[RequestContext] = None,
        authentication: Optional[GenericAuthentication] = None,
    ) -> bool:
        """Check client connectivity by executing a simple query."""
        client = self._client_manager.get(Connection.ASYNC)
        try:
            if isinstance(client, AsyncElasticsearch):
                return await client.ping()
            elif isinstance(client, AsyncIOMotorClient):
                db = client.get_database(str(self._config.connection.database))
                await db.command("ping")
                return True
            elif isinstance(client, AsyncRedis):
                await client.ping()
                return True
            else:
                raise TypeError(f"Invalid client type: '{type(client)}'")
        except Exception:
            print("Unable to check client connection:\n", traceback.format_exc())
            return False

    def sync_check_connection(
        self,
        operation_id: OptionalUUID = None,
        request_context: Optional[RequestContext] = None,
        authentication: Optional[GenericAuthentication] = None,
    ) -> bool:
        """Check client connectivity by executing a simple query."""
        client = self._client_manager.get(Connection.SYNC)
        try:
            if isinstance(client, Elasticsearch):
                return client.ping()
            elif isinstance(client, MongoClient):
                db = client.get_database(str(self._config.connection.database))
                db.command("ping")
                return True
            elif isinstance(client, SyncRedis):
                client.ping()
                return True
            else:
                raise TypeError(f"Invalid client type: '{type(client)}'")
        except Exception:
            print("Unable to check client connection:\n", traceback.format_exc())
            return False

    async def dispose(self):
        await self._client_manager.dispose()


class ElasticsearchDatabaseManager(
    NoSQLDatabaseManager[ElasticsearchConfig, AsyncElasticsearch, Elasticsearch]
):
    pass


class MongoDBDatabaseManager(
    NoSQLDatabaseManager[MongoDBConfig, AsyncIOMotorClient, MongoClient]
):
    pass


class RedisDatabaseManager(NoSQLDatabaseManager[RedisConfig, AsyncRedis, SyncRedis]):
    pass


NoSQLDatabaseManagerT = TypeVar(
    "NoSQLDatabaseManagerT",
    ElasticsearchDatabaseManager,
    MongoDBDatabaseManager,
    RedisDatabaseManager,
)


GenericDatabaseManagerT = TypeVar(
    "GenericDatabaseManagerT", SQLDatabaseManager, NoSQLDatabaseManager
)


SpecificDatabaseManagerT = TypeVar(
    "SpecificDatabaseManagerT",
    MySQLDatabaseManager,
    PostgreSQLDatabaseManager,
    SQLiteDatabaseManager,
    SQLServerDatabaseManager,
    ElasticsearchDatabaseManager,
    MongoDBDatabaseManager,
    RedisDatabaseManager,
)
