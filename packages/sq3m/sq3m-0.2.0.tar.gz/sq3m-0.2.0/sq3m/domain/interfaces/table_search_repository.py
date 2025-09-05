from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sq3m.domain.entities.table_summary import SearchResult, TableSummary


class TableSearchRepository(ABC):
    """Interface for table summary storage and hybrid search."""

    @abstractmethod
    def initialize_storage(self) -> None:
        """Initialize the storage (create tables, indexes, etc.)."""
        pass

    @abstractmethod
    def store_table_summary(self, table_summary: TableSummary) -> None:
        """Store a table summary with its embedding."""
        pass

    @abstractmethod
    def store_table_summaries(self, table_summaries: list[TableSummary]) -> None:
        """Store multiple table summaries."""
        pass

    @abstractmethod
    def search_tables_hybrid(
        self,
        query: str,
        query_embedding: list[float],
        limit: int = 10,
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3,
    ) -> list[SearchResult]:
        """
        Perform hybrid search using both vector similarity and keyword search.

        Args:
            query: Natural language query
            query_embedding: Embedding vector for the query
            limit: Maximum number of results to return
            vector_weight: Weight for vector search results (0.0 to 1.0)
            keyword_weight: Weight for keyword search results (0.0 to 1.0)

        Returns:
            List of search results sorted by relevance score
        """
        pass

    @abstractmethod
    def search_tables_vector(
        self, query_embedding: list[float], limit: int = 10
    ) -> list[SearchResult]:
        """Search tables using vector similarity only."""
        pass

    @abstractmethod
    def search_tables_keyword(self, query: str, limit: int = 10) -> list[SearchResult]:
        """Search tables using keyword/full-text search only."""
        pass

    @abstractmethod
    def get_all_table_summaries(self) -> list[TableSummary]:
        """Get all stored table summaries."""
        pass

    @abstractmethod
    def clear_table_summaries(self) -> None:
        """Clear all stored table summaries."""
        pass
