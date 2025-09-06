from abc import abstractmethod
from typing import Protocol


class AbstractDatabaseRepository(Protocol):
    @abstractmethod
    async def add_one(self, **data):
        raise NotImplementedError