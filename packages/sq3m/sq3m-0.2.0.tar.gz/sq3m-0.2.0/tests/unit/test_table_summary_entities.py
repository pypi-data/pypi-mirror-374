"""Tests for table summary entities."""

from __future__ import annotations

from sq3m.domain.entities.table_summary import SearchResult, TableSummary


class TestTableSummary:
    """Test cases for TableSummary entity."""

    def test_table_summary_creation(self):
        """Test basic TableSummary creation."""
        summary = TableSummary(
            table_name="users",
            summary="Users table with id, name, email columns",
            purpose="Store user information",
        )

        assert summary.table_name == "users"
        assert summary.summary == "Users table with id, name, email columns"
        assert summary.purpose == "Store user information"
        assert summary.embedding is None

    def test_table_summary_with_embedding(self):
        """Test TableSummary with embedding vector."""
        embedding = [0.1, -0.3, 0.8, 0.2]
        summary = TableSummary(
            table_name="orders",
            summary="Orders table",
            purpose="Store order data",
            embedding=embedding,
        )

        assert summary.embedding == embedding

    def test_table_summary_to_dict(self):
        """Test TableSummary to_dict conversion."""
        embedding = [0.1, -0.3, 0.8]
        summary = TableSummary(
            table_name="products",
            summary="Products table",
            purpose="Store product catalog",
            embedding=embedding,
        )

        result = summary.to_dict()

        expected = {
            "table_name": "products",
            "summary": "Products table",
            "purpose": "Store product catalog",
            "embedding": [0.1, -0.3, 0.8],
        }

        assert result == expected

    def test_table_summary_from_dict(self):
        """Test TableSummary from_dict creation."""
        data = {
            "table_name": "categories",
            "summary": "Categories table",
            "purpose": "Store product categories",
            "embedding": [0.5, -0.2, 0.7],
        }

        summary = TableSummary.from_dict(data)

        assert summary.table_name == "categories"
        assert summary.summary == "Categories table"
        assert summary.purpose == "Store product categories"
        assert summary.embedding == [0.5, -0.2, 0.7]

    def test_table_summary_from_dict_minimal(self):
        """Test TableSummary from_dict with minimal data."""
        data = {"table_name": "logs", "summary": "Application logs"}

        summary = TableSummary.from_dict(data)

        assert summary.table_name == "logs"
        assert summary.summary == "Application logs"
        assert summary.purpose is None
        assert summary.embedding is None


class TestSearchResult:
    """Test cases for SearchResult entity."""

    def test_search_result_creation(self):
        """Test SearchResult creation."""
        table_summary = TableSummary(
            table_name="users", summary="Users table", purpose="Store users"
        )

        result = SearchResult(
            table_summary=table_summary, score=0.85, search_type="hybrid"
        )

        assert result.table_summary == table_summary
        assert result.score == 0.85
        assert result.search_type == "hybrid"

    def test_search_result_different_types(self):
        """Test SearchResult with different search types."""
        table_summary = TableSummary(table_name="orders", summary="Orders table")

        vector_result = SearchResult(table_summary, 0.9, "vector")
        keyword_result = SearchResult(table_summary, 0.7, "keyword")
        hybrid_result = SearchResult(table_summary, 0.85, "hybrid")

        assert vector_result.search_type == "vector"
        assert keyword_result.search_type == "keyword"
        assert hybrid_result.search_type == "hybrid"

    def test_search_result_score_bounds(self):
        """Test SearchResult with various score values."""
        table_summary = TableSummary("test", "test summary")

        # Test different score ranges
        high_score = SearchResult(table_summary, 1.0, "vector")
        low_score = SearchResult(table_summary, 0.0, "vector")
        mid_score = SearchResult(table_summary, 0.5, "vector")

        assert high_score.score == 1.0
        assert low_score.score == 0.0
        assert mid_score.score == 0.5
