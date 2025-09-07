from elasticsearch import AsyncElasticsearch, Elasticsearch
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from redis.asyncio import Redis as AsyncRedis
from redis import Redis as SyncRedis
from typing import Generic, Literal, Tuple, TypeVar, Union, overload
from ..config import (
    ElasticsearchDatabaseConfig,
    MongoDBDatabaseConfig,
    RedisDatabaseConfig,
    NoSQLConfigT,
)
from ..enums import Connection


AsyncClientT = TypeVar(
    "AsyncClientT", AsyncElasticsearch, AsyncIOMotorClient, AsyncRedis
)


SyncClientT = TypeVar("SyncClientT", Elasticsearch, MongoClient, SyncRedis)


class ClientManager(
    Generic[
        NoSQLConfigT,
        AsyncClientT,
        SyncClientT,
    ]
):
    def __init__(self, config: NoSQLConfigT) -> None:
        super().__init__()
        self._config = config

        self._async_client = self._config.create_client(Connection.ASYNC)
        self._sync_client = self._config.create_client(Connection.SYNC)

    @overload
    def get(self, connection: Literal[Connection.ASYNC]) -> AsyncClientT: ...
    @overload
    def get(self, connection: Literal[Connection.SYNC]) -> SyncClientT: ...
    def get(
        self, connection: Connection = Connection.ASYNC
    ) -> Union[AsyncClientT, SyncClientT]:
        if connection is Connection.ASYNC:
            return self._async_client
        elif connection is Connection.SYNC:
            return self._sync_client

    def get_all(self) -> Tuple[AsyncClientT, SyncClientT]:
        return (self._async_client, self._sync_client)

    async def dispose(self):
        if isinstance(self._async_client, AsyncIOMotorClient):
            self._async_client.close()
        else:
            await self._async_client.close()
        self._sync_client.close()


class ElasticsearchClientManager(
    ClientManager[ElasticsearchDatabaseConfig, AsyncElasticsearch, Elasticsearch]
):
    pass


class MongoDBClientManager(
    ClientManager[MongoDBDatabaseConfig, AsyncIOMotorClient, MongoClient]
):
    pass


class RedisClientManager(ClientManager[RedisDatabaseConfig, AsyncRedis, SyncRedis]):
    pass


ClientManagerT = TypeVar(
    "ClientManagerT",
    ElasticsearchClientManager,
    MongoDBClientManager,
    RedisClientManager,
)
