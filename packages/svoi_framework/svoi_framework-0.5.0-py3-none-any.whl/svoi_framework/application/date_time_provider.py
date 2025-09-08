import abc
from datetime import datetime

import pytz


class DateTimeProvider(abc.ABC):
    @abc.abstractmethod
    def utc_now(self) -> datetime: ...


class DefaultDateTimeProvider(DateTimeProvider):
    def utc_now(self) -> datetime:
        return datetime.now(pytz.UTC)
