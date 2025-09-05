from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any

from sq3m.domain.entities.table_summary import SearchResult, TableSummary
from sq3m.infrastructure.database.sqlite_table_search_repository import (
    SQLiteTableSearchRepository,
)
from sq3m.infrastructure.llm.embedding_service import (
    EmbeddingService,
    EmbeddingServiceError,
)

if TYPE_CHECKING:
    from sq3m.domain.entities.database import Table
    from sq3m.domain.interfaces.table_search_repository import TableSearchRepository


class TableSearchService:
    """Service for managing table summaries and hybrid search."""

    def __init__(
        self,
        openai_api_key: str,
        embedding_model: str = "text-embedding-3-small",
        search_repository: TableSearchRepository | None = None,
        db_path: str = "table_search.db",
    ):
        self.embedding_service = EmbeddingService(openai_api_key, embedding_model)
        self.search_repository = search_repository or SQLiteTableSearchRepository(
            db_path
        )
        self._initialized = False

    def initialize(self) -> None:
        """Initialize the search repository."""
        if not self._initialized:
            self.search_repository.initialize_storage()
            self._initialized = True

    def create_table_summary(self, table: Table) -> TableSummary:
        """Create a comprehensive summary for a table."""
        # Build comprehensive summary text
        summary_parts = [f"Table: {table.name}"]

        if table.purpose:
            summary_parts.append(f"Purpose: {table.purpose}")

        if table.comment:
            summary_parts.append(f"Description: {table.comment}")

        # Add column information
        column_info = []
        for col in table.columns:
            col_desc = f"{col.name} ({col.data_type})"
            if col.is_primary_key:
                col_desc += " [PK]"
            if col.comment:
                col_desc += f" - {col.comment}"
            column_info.append(col_desc)

        if column_info:
            summary_parts.append(f"Columns: {', '.join(column_info)}")

        # Add sample data context if available
        if table.sample_rows:
            sample_context = self._extract_sample_context(table.sample_rows)
            if sample_context:
                summary_parts.append(f"Sample data context: {sample_context}")

        summary = " | ".join(summary_parts)

        return TableSummary(
            table_name=table.name, summary=summary, purpose=table.purpose
        )

    def _extract_sample_context(self, sample_rows: list[dict[str, Any]]) -> str:
        """Extract meaningful context from sample data."""
        if not sample_rows:
            return ""

        context_parts = []

        # Get column names
        if sample_rows:
            columns = list(sample_rows[0].keys())
            context_parts.append(f"contains columns: {', '.join(columns)}")

        # Add row count context
        row_count = len(sample_rows)
        if row_count > 0:
            context_parts.append(f"has {row_count} sample rows")

        return " ".join(context_parts)

    def store_table_summaries_with_embeddings(self, tables: list[Table]) -> None:
        """
        Create summaries for tables, generate embeddings, and store them.

        Raises:
            SystemExit: When OpenAI API fails during embedding generation
        """
        self.initialize()

        table_summaries = []
        summary_texts = []

        # Create summaries
        for table in tables:
            summary = self.create_table_summary(table)
            table_summaries.append(summary)
            summary_texts.append(summary.summary)

        # Generate embeddings in batch for efficiency
        try:
            print(f"🔄 Generating embeddings for {len(summary_texts)} tables...")
            embeddings = self.embedding_service.generate_embeddings_batch(summary_texts)

            # Attach embeddings to summaries
            for summary, embedding in zip(table_summaries, embeddings, strict=False):
                summary.embedding = embedding

            print("✅ Successfully generated embeddings for all tables")

        except EmbeddingServiceError as e:
            print(f"❌ Critical error: {e}")
            print("❌ Cannot continue without embeddings. Exiting...")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Unexpected error during embedding generation: {e}")
            print("❌ Cannot continue without embeddings. Exiting...")
            sys.exit(1)

        # Store all summaries
        self.search_repository.store_table_summaries(table_summaries)

    def search_relevant_tables(
        self,
        natural_language_query: str,
        limit: int = 10,
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3,
    ) -> list[SearchResult]:
        """
        Search for tables most relevant to the natural language query.

        Args:
            natural_language_query: User's query in natural language
            limit: Maximum number of tables to return
            vector_weight: Weight for semantic similarity (0.0 to 1.0)
            keyword_weight: Weight for keyword matching (0.0 to 1.0)

        Returns:
            List of search results ordered by relevance
        """
        self.initialize()

        try:
            # Generate embedding for the query
            query_embedding = self.embedding_service.generate_embedding(
                natural_language_query
            )

            # Perform hybrid search
            return self.search_repository.search_tables_hybrid(
                natural_language_query,
                query_embedding,
                limit,
                vector_weight,
                keyword_weight,
            )
        except EmbeddingServiceError as e:
            print(f"Warning: Embedding generation failed: {e}")
            print("Falling back to keyword-only search...")
            # Fallback to keyword search only
            return self.search_repository.search_tables_keyword(
                natural_language_query, limit
            )
        except Exception as e:
            print(f"Warning: Unexpected error during search: {e}")
            print("Falling back to keyword-only search...")
            # Fallback to keyword search only
            return self.search_repository.search_tables_keyword(
                natural_language_query, limit
            )

    def get_tables_for_query(
        self, natural_language_query: str, all_tables: list[Table], limit: int = 10
    ) -> list[Table]:
        """
        Get the most relevant tables for a query, falling back to all tables if search fails.

        Args:
            natural_language_query: User's query
            all_tables: Complete list of available tables
            limit: Maximum number of tables to return

        Returns:
            List of most relevant tables
        """
        try:
            # Search for relevant tables
            search_results = self.search_relevant_tables(natural_language_query, limit)

            if not search_results:
                # No search results, return all tables (up to limit)
                return all_tables[:limit]

            # Map search results back to Table objects
            relevant_tables = []
            table_name_map = {table.name: table for table in all_tables}

            for result in search_results:
                table = table_name_map.get(result.table_summary.table_name)
                if table:
                    relevant_tables.append(table)

            # If we don't have enough tables from search, fill with remaining tables
            if len(relevant_tables) < limit:
                used_table_names = {table.name for table in relevant_tables}
                remaining_tables = [
                    table for table in all_tables if table.name not in used_table_names
                ]
                relevant_tables.extend(remaining_tables[: limit - len(relevant_tables)])

            return relevant_tables[:limit]

        except Exception as e:
            print(f"Warning: Table search failed, using all tables: {e}")
            # Fallback to all tables
            return all_tables[:limit]

    def clear_storage(self) -> None:
        """Clear all stored table summaries."""
        self.initialize()
        self.search_repository.clear_table_summaries()

    def get_all_summaries(self) -> list[TableSummary]:
        """Get all stored table summaries."""
        self.initialize()
        return self.search_repository.get_all_table_summaries()
