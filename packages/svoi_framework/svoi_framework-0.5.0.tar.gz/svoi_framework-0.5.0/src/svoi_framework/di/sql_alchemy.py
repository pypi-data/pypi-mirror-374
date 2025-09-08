import asyncio

from dishka import Provider, provide, Scope, make_async_container
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import sessionmaker


class DbConfig(BaseModel):
    host: str
    port: int
    username: str
    password: str
    database: str
    ssl_mode: str = "disable"
    echo: bool = False


class SQLAlchemyProvider(Provider):
    def __init__(self, config: DbConfig) -> None:
        super().__init__()
        self._config = config

    @provide(scope=Scope.APP)
    async def async_engine(self) -> AsyncEngine:
        cfg = self._config
        return create_async_engine(
            f"postgresql+asyncpg://{cfg.username}:{cfg.password}@{cfg.host}:{cfg.port}/{cfg.database}",
        )

    @provide(scope=Scope.REQUEST)
    async def async_session(self, engine: AsyncEngine) -> AsyncSession:
        return AsyncSession(engine, expire_on_commit=False)


class SQLAlchemyProviderForTests(Provider):
    @provide(scope=Scope.APP)
    async def async_engine(self) -> AsyncEngine:
        return create_async_engine(
            f"sqlite+aiosqlite://:memory:",
        )

    @provide(scope=Scope.REQUEST)
    async def async_session(self, engine: AsyncEngine) -> AsyncSession:
        return AsyncSession(engine, expire_on_commit=False)
