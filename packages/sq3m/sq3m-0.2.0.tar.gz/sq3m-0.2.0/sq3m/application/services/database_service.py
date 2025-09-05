from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sq3m.application.services.table_search_service import TableSearchService
from sq3m.application.use_cases.database_analyzer import DatabaseAnalyzer
from sq3m.application.use_cases.sql_generator import SQLGenerator
from sq3m.infrastructure.database.repository_factory import DatabaseRepositoryFactory
from sq3m.infrastructure.history.markdown_history import MarkdownHistory
from sq3m.infrastructure.llm.translation_service import TranslationService

if TYPE_CHECKING:
    from sq3m.domain.entities.database import (
        DatabaseConnection,
        SQLQuery,
        Table,
    )
    from sq3m.domain.interfaces.database_repository import DatabaseRepository
    from sq3m.domain.interfaces.llm_service import LLMService


class DatabaseService:
    def __init__(self, llm_service: LLMService, openai_api_key: str | None = None):
        self.llm_service = llm_service
        self.database_repository: DatabaseRepository | None = None
        self.database_analyzer: DatabaseAnalyzer | None = None
        self.sql_generator: SQLGenerator | None = None
        self.tables_cache: list[Table] = []
        self.history = MarkdownHistory()

        # Initialize table search service if OpenAI API key is provided
        self.table_search_service: TableSearchService | None = None
        # Initialize translation service if OpenAI API key is provided
        self.translation_service: TranslationService | None = None
        if openai_api_key:
            self.table_search_service = TableSearchService(openai_api_key)
            self.translation_service = TranslationService(openai_api_key)

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

        # Check for existing summaries before doing expensive MySQL analysis
        if self.table_search_service:
            try:
                existing_summaries = self.table_search_service.get_all_summaries()

                if existing_summaries and len(existing_summaries) > 0:
                    print(
                        f"✅ Found existing {len(existing_summaries)} table summaries, skipping analysis"
                    )

                    # Create minimal tables cache from existing summaries (no MySQL queries needed)
                    from sq3m.domain.entities.database import Table

                    self.tables_cache = []
                    for summary in existing_summaries:
                        table = Table(
                            name=summary.table_name,
                            columns=[],
                            indexes=[],
                            purpose=summary.purpose,
                        )
                        self.tables_cache.append(table)

                    return {
                        summary.table_name: summary.purpose
                        for summary in existing_summaries
                    }

            except Exception as e:
                print(f"Warning: Could not check existing summaries: {e}")

        # Only if no existing summaries, do the full schema analysis
        schema = self.database_analyzer.analyze_schema()
        self.tables_cache = schema.tables

        # Store new summaries for future use
        if self.table_search_service:
            try:
                self.table_search_service.store_table_summaries_with_embeddings(
                    self.tables_cache
                )
                print(
                    f"✅ Stored {len(self.tables_cache)} table summaries for hybrid search"
                )
            except Exception as e:
                print(f"Warning: Failed to store table summaries for search: {e}")

        return self.database_analyzer.get_table_purposes()

    def _update_tables_with_existing_summaries(self, existing_summaries: list) -> None:
        """Update tables cache with purposes from existing summaries."""
        from sq3m.domain.entities.table_summary import TableSummary

        # Create a mapping of table names to purposes from existing summaries
        summary_purposes = {}
        for summary in existing_summaries:
            if isinstance(summary, TableSummary):
                summary_purposes[summary.table_name] = summary.purpose

        # Update tables cache with existing purposes
        for table in self.tables_cache:
            if table.name in summary_purposes:
                table.purpose = summary_purposes[table.name]

    def _translate_if_needed(self, natural_language: str) -> str:
        """Translate query to English if it's not already in English."""
        if not self.translation_service:
            return natural_language

        try:
            return self.translation_service.translate_to_english(natural_language)
        except Exception as e:
            print(f"Warning: Translation failed: {e}, using original query")
            return natural_language

    def generate_sql_from_natural_language(self, natural_language: str) -> SQLQuery:
        if not self.sql_generator:
            raise ValueError("Database not connected")

        # Translate to English if not already English
        translated_query = self._translate_if_needed(natural_language)

        # Use hybrid search to find most relevant tables if available
        tables_to_use = self.tables_cache
        if self.table_search_service:
            try:
                relevant_tables = self.table_search_service.get_tables_for_query(
                    translated_query, self.tables_cache, limit=10
                )
                if relevant_tables:
                    tables_to_use = relevant_tables
                    print(
                        f"🔍 Using {len(tables_to_use)} most relevant tables for query"
                    )
            except Exception as e:
                print(f"Warning: Table search failed, using all tables: {e}")

        return self.sql_generator.generate_sql(translated_query, tables_to_use)

    def execute_query(self, sql: str) -> Any:
        if not self.database_repository:
            raise ValueError("Database not connected")

        return self.database_repository.execute_query(sql)

    def generate_and_execute_query(
        self, natural_language: str, max_retries: int = 2
    ) -> Any:
        if not self.sql_generator:
            raise ValueError("Database not connected")

        # Translate to English if not already English
        translated_query = self._translate_if_needed(natural_language)

        # Use hybrid search to find most relevant tables if available
        tables_to_use = self.tables_cache
        if self.table_search_service:
            try:
                relevant_tables = self.table_search_service.get_tables_for_query(
                    translated_query, self.tables_cache, limit=10
                )
                if relevant_tables:
                    tables_to_use = relevant_tables
                    print(
                        f"🔍 Using {len(tables_to_use)} most relevant tables for execution"
                    )
            except Exception as e:
                print(f"Warning: Table search failed, using all tables: {e}")

        return self.sql_generator.generate_and_execute(
            translated_query, tables_to_use, max_retries
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
