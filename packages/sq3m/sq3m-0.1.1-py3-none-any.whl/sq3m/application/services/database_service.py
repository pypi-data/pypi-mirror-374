from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sq3m.application.use_cases.database_analyzer import DatabaseAnalyzer
from sq3m.application.use_cases.sql_generator import SQLGenerator
from sq3m.infrastructure.database.repository_factory import DatabaseRepositoryFactory
from sq3m.infrastructure.history.markdown_history import MarkdownHistory

if TYPE_CHECKING:
    from sq3m.domain.entities.database import (
        DatabaseConnection,
        SQLQuery,
        Table,
    )
    from sq3m.domain.interfaces.database_repository import DatabaseRepository
    from sq3m.domain.interfaces.llm_service import LLMService


class DatabaseService:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.database_repository: DatabaseRepository | None = None
        self.database_analyzer: DatabaseAnalyzer | None = None
        self.sql_generator: SQLGenerator | None = None
        self.tables_cache: list[Table] = []
        self.history = MarkdownHistory()

    def connect_to_database(self, connection: DatabaseConnection) -> bool:
        try:
            self.database_repository = DatabaseRepositoryFactory.create(
                connection.database_type
            )

            # Test connection first
            if not self.database_repository.test_connection(connection):
                return False

            # Establish connection
            self.database_repository.connect(connection)

            # Initialize use cases
            self.database_analyzer = DatabaseAnalyzer(
                self.database_repository, self.llm_service
            )
            self.sql_generator = SQLGenerator(
                self.database_repository, self.llm_service, self.history
            )

            return True
        except Exception:
            return False

    def analyze_database_schema(self) -> Any:
        if not self.database_analyzer:
            raise ValueError("Database not connected")

        schema = self.database_analyzer.analyze_schema()
        self.tables_cache = schema.tables
        return self.database_analyzer.get_table_purposes()

    def generate_sql_from_natural_language(self, natural_language: str) -> SQLQuery:
        if not self.sql_generator:
            raise ValueError("Database not connected")

        return self.sql_generator.generate_sql(natural_language, self.tables_cache)

    def execute_query(self, sql: str) -> Any:
        if not self.database_repository:
            raise ValueError("Database not connected")

        return self.database_repository.execute_query(sql)

    def generate_and_execute_query(
        self, natural_language: str, max_retries: int = 2
    ) -> Any:
        if not self.sql_generator:
            raise ValueError("Database not connected")

        return self.sql_generator.generate_and_execute(
            natural_language, self.tables_cache, max_retries
        )

    def get_tables(self) -> list[Table]:
        return self.tables_cache.copy()

    def disconnect(self) -> None:
        if self.database_repository:
            self.database_repository.disconnect()
            self.database_repository = None
            self.database_analyzer = None
            self.sql_generator = None
            self.tables_cache = []
