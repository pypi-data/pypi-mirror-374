from unittest import mock

import pytest

from .user_test_repository import (
    UserTestRepository,
    UserTestAggregate,
    UserTestEvent,
)


@pytest.mark.asyncio
async def test_add_happy_path(
    user_test_repository: UserTestRepository,
    mock_async_session: mock.MagicMock,
    some_user: UserTestAggregate,
) -> None:
    some_user.add_event("123")
    await user_test_repository.add(some_user)
    events = user_test_repository.collect_events()

    assert len(events) == 1
    assert isinstance(events[0], UserTestEvent)
    assert events[0].value == "123"  # type: ignore

    assert mock_async_session.add.call_args[0][0].user_id == some_user.id
