import abc
import uuid


class UUIDProvider(abc.ABC):
    @abc.abstractmethod
    def generate(self) -> uuid.UUID: ...


class DefaultUUIDProvider(UUIDProvider):
    def generate(self) -> uuid.UUID:
        return uuid.uuid4()
