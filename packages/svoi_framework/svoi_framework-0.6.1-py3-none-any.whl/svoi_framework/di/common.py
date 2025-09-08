from dishka import Provider, Scope, provide

from svoi_framework.application.date_time_provider import (
    DefaultDateTimeProvider,
    DateTimeProvider,
)
from svoi_framework.application.uuid_provider import DefaultUUIDProvider, UUIDProvider


class CommonProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def uuid_provider(self) -> UUIDProvider:
        return DefaultUUIDProvider()

    @provide(scope=Scope.REQUEST)
    def date_time_provider(self) -> DateTimeProvider:
        return DefaultDateTimeProvider()
