from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sq3m.domain.entities.database import DatabaseSchema, Table
    from sq3m.domain.interfaces.database_repository import DatabaseRepository
    from sq3m.domain.interfaces.llm_service import LLMService


class DatabaseAnalyzer:
    def __init__(
        self, database_repository: DatabaseRepository, llm_service: LLMService
    ):
        self.database_repository = database_repository
        self.llm_service = llm_service
        self.table_purposes: dict[str, str] = {}

    async def analyze_schema_async(self) -> DatabaseSchema:
        schema = self.database_repository.get_schema()

        # Create async tasks for all table analysis
        tasks = []
        for table in schema.tables:
            task = self._analyze_table_async(table)
            tasks.append(task)

        # Wait for all tasks to complete
        analyzed_tables = await asyncio.gather(*tasks)

        # Update schema with analyzed tables
        schema.tables = analyzed_tables

        return schema

    async def _analyze_table_async(self, table: Table) -> Table:
        # Get sample rows for better analysis
        try:
            sample_rows = self.database_repository.get_table_sample_rows(
                table.name, limit=5
            )
            table.sample_rows = sample_rows
        except Exception:
            table.sample_rows = []

        # Use async method for better performance
        purpose = await self.llm_service.infer_table_purpose_async(table)
        table.purpose = purpose
        self.table_purposes[table.name] = purpose

        return table

    def analyze_schema(self) -> DatabaseSchema:
        schema = self.database_repository.get_schema()

        # Analyze each table's purpose using LLM
        for table in schema.tables:
            # Get sample rows for better analysis
            try:
                sample_rows = self.database_repository.get_table_sample_rows(
                    table.name, limit=5
                )
                table.sample_rows = sample_rows
            except Exception:
                table.sample_rows = []

            purpose = self.llm_service.infer_table_purpose(table)
            table.purpose = purpose
            self.table_purposes[table.name] = purpose

        return schema

    def get_table_purposes(self) -> dict[str, str]:
        return self.table_purposes.copy()

    def get_tables_with_purposes(self) -> list[Table]:
        schema = self.database_repository.get_schema()
        for table in schema.tables:
            if table.name in self.table_purposes:
                table.purpose = self.table_purposes[table.name]
        return schema.tables
