import uuid
from typing import AsyncGenerator
from unittest import mock

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession

from svoi_framework.unit_of_work.uow import EventPublisher
from .user_test_repository import (
    SqlAlchemyTestUnitOfWork,
    Base,
    UserTestRepository,
    UserTestAggregate,
)


@pytest_asyncio.fixture(scope="package")
async def async_engine() -> AsyncGenerator[AsyncEngine]:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=True,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose(close=True)


@pytest_asyncio.fixture(scope="function")
async def async_session(async_engine: AsyncEngine) -> AsyncSession:
    return AsyncSession(async_engine, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function")
async def mock_async_session(async_engine: AsyncEngine) -> AsyncSession:
    return mock.MagicMock(spec=AsyncSession)


@pytest.fixture(scope="function")
def mock_event_dispatcher() -> EventPublisher:
    return mock.MagicMock(spec=EventPublisher)


@pytest.fixture(scope="function")
def unit_of_work(
    async_session: AsyncSession,
    mock_event_dispatcher: EventPublisher,
) -> SqlAlchemyTestUnitOfWork:
    return SqlAlchemyTestUnitOfWork(mock_event_dispatcher, async_session)


@pytest_asyncio.fixture(scope="function")
async def user_test_repository(mock_async_session: AsyncSession) -> UserTestRepository:
    return UserTestRepository(mock_async_session)


@pytest.fixture(scope="function")
def some_user() -> UserTestAggregate:
    return UserTestAggregate(
        user_id=uuid.uuid4(),
        first_name="John",
        last_name="Doe",
    )
