from typing import AsyncGenerator

import asyncpg
from dishka import Provider, provide, Scope

from svoi_framework.di.sql_alchemy import DbConfig


class AsyncPgProvider(Provider):

    def __init__(self, db: DbConfig):
        super().__init__()
        self.db = db

    @provide(scope=Scope.APP)
    async def connection_pool(self) -> asyncpg.Pool:
        dsn = (
            "postgresql://{user}:{password}@{host}:{port}/{database}"
            .format(
                user=self.db.username,
                password=self.db.password,
                host=self.db.host,
                port=self.db.port,
                database=self.db.database
            )
        )
        return asyncpg.create_pool(dsn)

    @provide(scope=Scope.REQUEST)
    async def connection(self, pool: asyncpg.Pool) -> AsyncGenerator[asyncpg.Connection]:
        async with pool.acquire() as conn:
            yield conn  # type: ignore
