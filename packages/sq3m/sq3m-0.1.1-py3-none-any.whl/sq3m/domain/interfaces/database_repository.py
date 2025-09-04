from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sq3m.domain.entities.database import (
        DatabaseConnection,
        DatabaseSchema,
        Table,
    )


class DatabaseRepository(ABC):
    @abstractmethod
    def connect(self, connection: DatabaseConnection) -> None:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @abstractmethod
    def get_schema(self) -> DatabaseSchema:
        pass

    @abstractmethod
    def get_tables(self) -> list[Table]:
        pass

    @abstractmethod
    def execute_query(self, sql: str) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def test_connection(self, connection: DatabaseConnection) -> bool:
        pass

    @abstractmethod
    def get_table_sample_rows(
        self, table_name: str, limit: int = 10
    ) -> list[dict[str, Any]]:
        pass
