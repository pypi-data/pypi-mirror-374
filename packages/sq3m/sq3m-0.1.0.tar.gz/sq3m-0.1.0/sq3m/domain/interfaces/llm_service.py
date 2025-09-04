from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sq3m.domain.entities.database import SQLQuery, Table


class LLMService(ABC):
    @abstractmethod
    def infer_table_purpose(self, table: Table) -> str:
        pass

    @abstractmethod
    async def infer_table_purpose_async(self, table: Table) -> str:
        pass

    @abstractmethod
    def generate_sql(self, natural_language: str, tables: list[Table]) -> SQLQuery:
        pass

    @abstractmethod
    async def generate_sql_async(
        self, natural_language: str, tables: list[Table]
    ) -> SQLQuery:
        pass

    @abstractmethod
    def generate_sql_with_error_feedback(
        self,
        natural_language: str,
        tables: list[Table],
        previous_sql: str,
        error_message: str,
    ) -> SQLQuery:
        pass
