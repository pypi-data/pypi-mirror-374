"""Database abstraction layer."""

from abc import ABC, abstractmethod
from typing import Dict, Type, TypeVar

import pydantic


class DatabaseItem(ABC, pydantic.BaseModel):
    """Base class for database items."""

    model_config = pydantic.ConfigDict(revalidate_instances="always")

    @property
    @abstractmethod
    def identifier(self) -> str:
        """Database item identifier."""

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DatabaseItem):
            raise NotImplementedError
        return self.identifier == other.identifier

    def __hash__(self) -> int:
        return hash(self.identifier)


T = TypeVar("T", bound=DatabaseItem)


class DatabaseError(Exception):
    """Errors related to database operations."""


class UnknownEntityError(DatabaseError):
    """Requested entity does not exist."""


class Database(ABC):
    """Database abstraction."""

    @abstractmethod
    def update(self, item: DatabaseItem) -> None:
        """Update entity."""

    @abstractmethod
    def get(self, schema: Type[T], identifier: str) -> T:
        """Return entity, raise UnknownEntityError if entity does not exist."""

    @abstractmethod
    def get_all(self, schema: Type[T]) -> Dict[str, T]:
        """Return all entities of schema."""

    @abstractmethod
    def delete(self, item: DatabaseItem) -> None:
        """Delete entity."""

    @abstractmethod
    def find(self, schema: Type[T], **kwargs: str) -> Dict[str, T]:
        """Return all entities of schema matching the filter criteria."""


class DictDatabase(Database):
    """Simple Database implementation with dictionary."""

    def __init__(self) -> None:
        self.data: Dict[Type[DatabaseItem], Dict[str, DatabaseItem]] = {}

    def update(self, item: DatabaseItem) -> None:
        """Update data."""
        item_type = type(item)
        if item_type not in self.data:
            self.data[item_type] = {}
        self.data[item_type][item.identifier] = item

    def get(self, schema: Type[T], identifier: str) -> T:
        try:
            return self.data[schema][identifier]  # type: ignore
        except KeyError as exc:
            raise UnknownEntityError(f"Unknown identifier: {identifier}") from exc

    def get_all(self, schema: Type[T]) -> Dict[str, T]:
        try:
            return self.data[schema]  # type: ignore
        except KeyError as exc:
            raise DatabaseError(f"Unkonwn schema: {schema}") from exc
