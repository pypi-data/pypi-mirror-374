"""Tests for table search service."""

from __future__ import annotations

from unittest.mock import Mock, patch

from sq3m.application.services.table_search_service import TableSearchService
from sq3m.domain.entities.database import Column, Table
from sq3m.domain.entities.table_summary import SearchResult, TableSummary


class TestTableSearchService:
    """Test cases for TableSearchService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.api_key = "test-api-key"
        self.mock_repository = Mock()
        self.service = TableSearchService(
            self.api_key, search_repository=self.mock_repository
        )

    @patch("sq3m.application.services.table_search_service.EmbeddingService")
    def test_initialization_default(self, mock_embedding_service):
        """Test service initialization with defaults."""
        service = TableSearchService("test-key")

        mock_embedding_service.assert_called_once_with(
            "test-key", "text-embedding-3-small"
        )
        assert not service._initialized

    @patch("sq3m.application.services.table_search_service.EmbeddingService")
    def test_initialization_custom_params(self, mock_embedding_service):
        """Test service initialization with custom parameters."""
        mock_repo = Mock()
        service = TableSearchService(
            "test-key",
            embedding_model="custom-model",
            search_repository=mock_repo,
            db_path="custom.db",
        )

        mock_embedding_service.assert_called_once_with("test-key", "custom-model")
        assert service.search_repository == mock_repo

    def test_initialize(self):
        """Test service initialization."""
        self.service.initialize()

        self.mock_repository.initialize_storage.assert_called_once()
        assert self.service._initialized

    def test_initialize_once(self):
        """Test that initialize only runs once."""
        self.service.initialize()
        self.service.initialize()

        # Should only be called once
        assert self.mock_repository.initialize_storage.call_count == 1

    def test_create_table_summary_complete(self):
        """Test creating table summary with complete table information."""
        columns = [
            Column("id", "int", False, True, comment="Primary key"),
            Column("name", "varchar", False, False, comment="User name"),
            Column("email", "varchar", True, False),
        ]

        sample_rows = [
            {"id": 1, "name": "John", "email": "john@example.com"},
            {"id": 2, "name": "Jane", "email": "jane@example.com"},
        ]

        table = Table(
            name="users",
            columns=columns,
            indexes=[],
            comment="Users table",
            purpose="Store user information",
            sample_rows=sample_rows,
        )

        summary = self.service.create_table_summary(table)

        assert summary.table_name == "users"
        assert summary.purpose == "Store user information"
        assert "Table: users" in summary.summary
        assert "Purpose: Store user information" in summary.summary
        assert "Description: Users table" in summary.summary
        assert "id (int) [PK] - Primary key" in summary.summary
        assert "Sample data context" in summary.summary

    def test_create_table_summary_minimal(self):
        """Test creating table summary with minimal table information."""
        columns = [Column("data", "json", True, False)]
        table = Table(name="temp", columns=columns, indexes=[])

        summary = self.service.create_table_summary(table)

        assert summary.table_name == "temp"
        assert summary.purpose is None
        assert "Table: temp" in summary.summary
        assert "data (json)" in summary.summary

    def test_extract_sample_context(self):
        """Test extracting context from sample data."""
        sample_rows = [
            {"id": 1, "name": "test", "value": 100},
            {"id": 2, "name": "test2", "value": 200},
        ]

        context = self.service._extract_sample_context(sample_rows)

        assert "contains columns: id, name, value" in context
        assert "has 2 sample rows" in context

    def test_extract_sample_context_empty(self):
        """Test extracting context from empty sample data."""
        context = self.service._extract_sample_context([])
        assert context == ""

    @patch("sq3m.application.services.table_search_service.EmbeddingService")
    def test_store_table_summaries_with_embeddings_success(
        self, mock_embedding_service_class
    ):
        """Test successful storage of table summaries with embeddings."""
        # Mock embedding service
        mock_embedding_service = Mock()
        mock_embedding_service_class.return_value = mock_embedding_service
        mock_embedding_service.generate_embeddings_batch.return_value = [
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
        ]

        # Create test tables
        tables = [
            Table("users", [Column("id", "int", False, True)], []),
            Table("orders", [Column("id", "int", False, True)], []),
        ]

        service = TableSearchService("test-key", search_repository=self.mock_repository)
        service.store_table_summaries_with_embeddings(tables)

        # Verify repository calls
        self.mock_repository.initialize_storage.assert_called_once()
        self.mock_repository.store_table_summaries.assert_called_once()

        # Check stored summaries have embeddings
        stored_summaries = self.mock_repository.store_table_summaries.call_args[0][0]
        assert len(stored_summaries) == 2
        assert stored_summaries[0].embedding == [0.1, 0.2, 0.3]
        assert stored_summaries[1].embedding == [0.4, 0.5, 0.6]

    @patch("sq3m.application.services.table_search_service.EmbeddingService")
    @patch("sys.exit")
    def test_store_table_summaries_embedding_failure(
        self, mock_exit, mock_embedding_service_class
    ):
        """Test that embedding generation failures cause program to exit."""
        mock_embedding_service = Mock()
        mock_embedding_service_class.return_value = mock_embedding_service
        mock_embedding_service.generate_embeddings_batch.side_effect = Exception(
            "API Error"
        )

        tables = [Table("test", [Column("id", "int", False, True)], [])]

        service = TableSearchService("test-key", search_repository=self.mock_repository)

        # Should call sys.exit(1)
        service.store_table_summaries_with_embeddings(tables)

        # Verify sys.exit was called
        mock_exit.assert_called_once_with(1)

    @patch("sq3m.application.services.table_search_service.EmbeddingService")
    def test_search_relevant_tables_success(self, mock_embedding_service_class):
        """Test successful table search."""
        mock_embedding_service = Mock()
        mock_embedding_service_class.return_value = mock_embedding_service
        mock_embedding_service.generate_embedding.return_value = [0.1, 0.2, 0.3]

        # Mock repository response
        mock_search_results = [
            SearchResult(TableSummary("users", "Users table"), 0.9, "hybrid"),
            SearchResult(TableSummary("accounts", "Accounts table"), 0.7, "hybrid"),
        ]
        self.mock_repository.search_tables_hybrid.return_value = mock_search_results

        service = TableSearchService("test-key", search_repository=self.mock_repository)
        results = service.search_relevant_tables("find users", limit=5)

        assert len(results) == 2
        assert results[0].table_summary.table_name == "users"

        # Verify calls
        mock_embedding_service.generate_embedding.assert_called_once_with("find users")
        self.mock_repository.search_tables_hybrid.assert_called_once_with(
            "find users", [0.1, 0.2, 0.3], 5, 0.7, 0.3
        )

    @patch("sq3m.application.services.table_search_service.EmbeddingService")
    def test_search_relevant_tables_embedding_failure(
        self, mock_embedding_service_class
    ):
        """Test table search fallback when embedding generation fails."""
        mock_embedding_service = Mock()
        mock_embedding_service_class.return_value = mock_embedding_service
        mock_embedding_service.generate_embedding.side_effect = Exception("API Error")

        # Mock keyword search fallback
        mock_search_results = [
            SearchResult(TableSummary("users", "Users table"), 0.8, "keyword")
        ]
        self.mock_repository.search_tables_keyword.return_value = mock_search_results

        service = TableSearchService("test-key", search_repository=self.mock_repository)
        results = service.search_relevant_tables("find users", limit=5)

        assert len(results) == 1
        assert results[0].search_type == "keyword"

        # Should fallback to keyword search
        self.mock_repository.search_tables_keyword.assert_called_once_with(
            "find users", 5
        )

    def test_get_tables_for_query_success(self):
        """Test getting tables for query with successful search."""
        # Mock search results
        mock_search_results = [
            SearchResult(TableSummary("users", "Users table"), 0.9, "hybrid"),
            SearchResult(TableSummary("profiles", "User profiles"), 0.7, "hybrid"),
        ]

        # Create all tables
        all_tables = [
            Table("users", [], []),
            Table("profiles", [], []),
            Table("orders", [], []),
            Table("products", [], []),
        ]

        with patch.object(
            self.service, "search_relevant_tables", return_value=mock_search_results
        ):
            result_tables = self.service.get_tables_for_query(
                "user information", all_tables, limit=3
            )

        assert len(result_tables) == 3
        assert result_tables[0].name == "users"
        assert result_tables[1].name == "profiles"
        assert result_tables[2].name == "orders"  # Filled from remaining tables

    def test_get_tables_for_query_no_results(self):
        """Test getting tables when search returns no results."""
        all_tables = [
            Table("table1", [], []),
            Table("table2", [], []),
        ]

        with patch.object(self.service, "search_relevant_tables", return_value=[]):
            result_tables = self.service.get_tables_for_query(
                "test query", all_tables, limit=5
            )

        # Should return all tables up to limit
        assert len(result_tables) == 2
        assert result_tables == all_tables

    def test_get_tables_for_query_search_failure(self):
        """Test getting tables when search fails completely."""
        all_tables = [Table("table1", [], [])]

        with patch.object(
            self.service,
            "search_relevant_tables",
            side_effect=Exception("Search failed"),
        ):
            result_tables = self.service.get_tables_for_query(
                "test query", all_tables, limit=5
            )

        # Should fallback to all tables
        assert result_tables == all_tables

    def test_clear_storage(self):
        """Test clearing storage."""
        self.service.clear_storage()

        self.mock_repository.initialize_storage.assert_called_once()
        self.mock_repository.clear_table_summaries.assert_called_once()

    def test_get_all_summaries(self):
        """Test getting all summaries."""
        mock_summaries = [
            TableSummary("table1", "Summary 1"),
            TableSummary("table2", "Summary 2"),
        ]
        self.mock_repository.get_all_table_summaries.return_value = mock_summaries

        result = self.service.get_all_summaries()

        assert result == mock_summaries
        self.mock_repository.initialize_storage.assert_called_once()
        self.mock_repository.get_all_table_summaries.assert_called_once()

    def test_search_with_custom_weights(self):
        """Test search with custom vector/keyword weights."""
        with patch.object(
            self.service.embedding_service,
            "generate_embedding",
            return_value=[0.1, 0.2],
        ):
            self.service.search_relevant_tables(
                "test query", limit=5, vector_weight=0.8, keyword_weight=0.2
            )

            self.mock_repository.search_tables_hybrid.assert_called_once_with(
                "test query", [0.1, 0.2], 5, 0.8, 0.2
            )
