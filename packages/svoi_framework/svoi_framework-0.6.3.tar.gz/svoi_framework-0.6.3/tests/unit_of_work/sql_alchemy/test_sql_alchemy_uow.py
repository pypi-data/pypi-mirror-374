import uuid
from unittest import mock

import pytest

from .user_test_repository import (
    SqlAlchemyTestUnitOfWork,
    UserTestAggregate,
    UserTestEvent,
)


@pytest.mark.asyncio
async def test_uow_commited_dispatches_events(
    unit_of_work: SqlAlchemyTestUnitOfWork,
    mock_event_dispatcher: mock.MagicMock,
) -> None:
    async with unit_of_work:
        user = UserTestAggregate(uuid.uuid4(), "John", "Doe")
        user.add_event("test_event")
        await unit_of_work.user_repository.add(user)
        await unit_of_work.commit()

    mock_event_dispatcher.dispatch.assert_called_with(UserTestEvent("test_event"))


@pytest.mark.asyncio
async def test_uow_not_commited_events_not_dispatched(
    unit_of_work: SqlAlchemyTestUnitOfWork,
    mock_event_dispatcher: mock.MagicMock,
) -> None:
    async with unit_of_work:
        user = UserTestAggregate(uuid.uuid4(), "John", "Doe")
        user.add_event("test_event")
        await unit_of_work.user_repository.add(user)

    mock_event_dispatcher.dispatch.assert_not_called()
