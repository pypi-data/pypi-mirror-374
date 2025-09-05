"""Tests for table search service error handling and program termination."""

from __future__ import annotations

from unittest.mock import Mock, patch

from sq3m.application.services.table_search_service import TableSearchService
from sq3m.domain.entities.database import Column, Table
from sq3m.domain.entities.table_summary import SearchResult, TableSummary
from sq3m.infrastructure.llm.embedding_service import EmbeddingServiceError


class TestTableSearchServiceErrorHandling:
    """Test cases for table search service error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.api_key = "test-api-key"
        self.mock_repository = Mock()

    def create_test_table(self, name: str = "test_table") -> Table:
        """Create a test table for testing."""
        return Table(
            name=name,
            columns=[Column("id", "int", False, True)],
            indexes=[],
            purpose="Test table",
        )

    @patch("sq3m.application.services.table_search_service.EmbeddingService")
    @patch("sys.exit")
    @patch("builtins.print")
    def test_store_table_summaries_api_error_exits(
        self, mock_print, mock_exit, mock_embedding_service_class
    ):
        """Test that API errors during table summary storage cause program to exit."""
        # Mock embedding service to raise EmbeddingServiceError
        mock_embedding_service = Mock()
        mock_embedding_service_class.return_value = mock_embedding_service
        mock_embedding_service.generate_embeddings_batch.side_effect = (
            EmbeddingServiceError("OpenAI API error (status 401): Unauthorized")
        )

        service = TableSearchService(
            self.api_key, search_repository=self.mock_repository
        )

        test_table = self.create_test_table()

        # Should call sys.exit(1)
        service.store_table_summaries_with_embeddings([test_table])

        # Verify sys.exit was called with code 1
        mock_exit.assert_called_once_with(1)

        # Verify error messages were printed
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("❌ Critical error:" in call for call in print_calls)
        assert any(
            "❌ Cannot continue without embeddings. Exiting..." in call
            for call in print_calls
        )

    @patch("sq3m.application.services.table_search_service.EmbeddingService")
    @patch("sys.exit")
    @patch("builtins.print")
    def test_store_table_summaries_unexpected_error_exits(
        self, mock_print, mock_exit, mock_embedding_service_class
    ):
        """Test that unexpected errors during table summary storage cause program to exit."""
        # Mock embedding service to raise unexpected exception
        mock_embedding_service = Mock()
        mock_embedding_service_class.return_value = mock_embedding_service
        mock_embedding_service.generate_embeddings_batch.side_effect = RuntimeError(
            "Unexpected error"
        )

        service = TableSearchService(
            self.api_key, search_repository=self.mock_repository
        )

        test_table = self.create_test_table()

        # Should call sys.exit(1)
        service.store_table_summaries_with_embeddings([test_table])

        # Verify sys.exit was called with code 1
        mock_exit.assert_called_once_with(1)

        # Verify error messages were printed
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any(
            "❌ Unexpected error during embedding generation:" in call
            for call in print_calls
        )
        assert any(
            "❌ Cannot continue without embeddings. Exiting..." in call
            for call in print_calls
        )

    @patch("sq3m.application.services.table_search_service.EmbeddingService")
    @patch("builtins.print")
    def test_store_table_summaries_success_no_exit(
        self, mock_print, mock_embedding_service_class
    ):
        """Test that successful embedding generation does not cause program to exit."""
        # Mock successful embedding service
        mock_embedding_service = Mock()
        mock_embedding_service_class.return_value = mock_embedding_service
        mock_embedding_service.generate_embeddings_batch.return_value = [
            [0.1, 0.2, 0.3]
        ]

        service = TableSearchService(
            self.api_key, search_repository=self.mock_repository
        )

        test_table = self.create_test_table()

        # Should complete successfully without calling sys.exit
        service.store_table_summaries_with_embeddings([test_table])

        # Verify success messages were printed
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("🔄 Generating embeddings for" in call for call in print_calls)
        assert any(
            "✅ Successfully generated embeddings for all tables" in call
            for call in print_calls
        )

        # Verify repository was called to store summaries
        self.mock_repository.store_table_summaries.assert_called_once()

    @patch("sq3m.application.services.table_search_service.EmbeddingService")
    @patch("builtins.print")
    def test_search_relevant_tables_embedding_error_fallback(
        self, mock_print, mock_embedding_service_class
    ):
        """Test that search falls back to keyword search when embedding generation fails."""
        # Mock embedding service to fail on query embedding
        mock_embedding_service = Mock()
        mock_embedding_service_class.return_value = mock_embedding_service
        mock_embedding_service.generate_embedding.side_effect = EmbeddingServiceError(
            "API Error"
        )

        # Mock keyword search results
        mock_keyword_results = [
            SearchResult(TableSummary("test_table", "test summary"), 0.8, "keyword")
        ]
        self.mock_repository.search_tables_keyword.return_value = mock_keyword_results

        service = TableSearchService(
            self.api_key, search_repository=self.mock_repository
        )

        # Should fallback to keyword search
        results = service.search_relevant_tables("test query")

        # Verify keyword search was called
        self.mock_repository.search_tables_keyword.assert_called_once_with(
            "test query", 10
        )

        # Verify results are from keyword search
        assert len(results) == 1
        assert results[0].search_type == "keyword"

        # Verify warning messages were printed
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any(
            "Warning: Embedding generation failed:" in call for call in print_calls
        )
        assert any(
            "Falling back to keyword-only search..." in call for call in print_calls
        )

    @patch("sq3m.application.services.table_search_service.EmbeddingService")
    @patch("builtins.print")
    def test_search_relevant_tables_unexpected_error_fallback(
        self, mock_print, mock_embedding_service_class
    ):
        """Test that search falls back to keyword search on unexpected errors."""
        # Mock embedding service to raise unexpected error
        mock_embedding_service = Mock()
        mock_embedding_service_class.return_value = mock_embedding_service
        mock_embedding_service.generate_embedding.side_effect = ValueError(
            "Unexpected error"
        )

        # Mock keyword search results
        mock_keyword_results = [
            SearchResult(TableSummary("test_table", "test summary"), 0.7, "keyword")
        ]
        self.mock_repository.search_tables_keyword.return_value = mock_keyword_results

        service = TableSearchService(
            self.api_key, search_repository=self.mock_repository
        )

        # Should fallback to keyword search
        results = service.search_relevant_tables("test query")

        # Verify keyword search was called
        self.mock_repository.search_tables_keyword.assert_called_once_with(
            "test query", 10
        )

        # Verify results are from keyword search
        assert len(results) == 1
        assert results[0].search_type == "keyword"

        # Verify warning messages were printed
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any(
            "Warning: Unexpected error during search:" in call for call in print_calls
        )
        assert any(
            "Falling back to keyword-only search..." in call for call in print_calls
        )

    @patch("sq3m.application.services.table_search_service.EmbeddingService")
    def test_search_relevant_tables_success_no_fallback(
        self, mock_embedding_service_class
    ):
        """Test that successful search does not trigger fallback."""
        # Mock successful embedding service
        mock_embedding_service = Mock()
        mock_embedding_service_class.return_value = mock_embedding_service
        mock_embedding_service.generate_embedding.return_value = [0.1, 0.2, 0.3]

        # Mock hybrid search results
        mock_hybrid_results = [
            SearchResult(TableSummary("test_table", "test summary"), 0.9, "hybrid")
        ]
        self.mock_repository.search_tables_hybrid.return_value = mock_hybrid_results

        service = TableSearchService(
            self.api_key, search_repository=self.mock_repository
        )

        # Should use hybrid search successfully
        results = service.search_relevant_tables("test query")

        # Verify hybrid search was called
        self.mock_repository.search_tables_hybrid.assert_called_once_with(
            "test query", [0.1, 0.2, 0.3], 10, 0.7, 0.3
        )

        # Verify results are from hybrid search
        assert len(results) == 1
        assert results[0].search_type == "hybrid"

        # Verify keyword search was NOT called (no fallback)
        self.mock_repository.search_tables_keyword.assert_not_called()

    @patch("sq3m.application.services.table_search_service.EmbeddingService")
    @patch("sys.exit")
    def test_multiple_tables_one_failure_exits(
        self, mock_exit, mock_embedding_service_class
    ):
        """Test that failure with multiple tables still exits the program."""
        # Mock embedding service to fail
        mock_embedding_service = Mock()
        mock_embedding_service_class.return_value = mock_embedding_service
        mock_embedding_service.generate_embeddings_batch.side_effect = (
            EmbeddingServiceError("Batch API Error")
        )

        service = TableSearchService(
            self.api_key, search_repository=self.mock_repository
        )

        # Create multiple test tables
        test_tables = [
            self.create_test_table("table1"),
            self.create_test_table("table2"),
            self.create_test_table("table3"),
        ]

        # Should still call sys.exit(1) even with multiple tables
        service.store_table_summaries_with_embeddings(test_tables)

        # Verify sys.exit was called with code 1
        mock_exit.assert_called_once_with(1)

    @patch("sq3m.application.services.table_search_service.EmbeddingService")
    def test_get_tables_for_query_search_failure_fallback(
        self, mock_embedding_service_class
    ):
        """Test that get_tables_for_query falls back to all tables when search fails."""
        # Mock embedding service to fail
        mock_embedding_service = Mock()
        mock_embedding_service_class.return_value = mock_embedding_service

        service = TableSearchService(
            self.api_key, search_repository=self.mock_repository
        )

        # Mock search_relevant_tables to raise an exception
        with patch.object(
            service, "search_relevant_tables", side_effect=Exception("Search failed")
        ):
            all_tables = [
                self.create_test_table("table1"),
                self.create_test_table("table2"),
            ]

            # Should fallback to all tables
            result_tables = service.get_tables_for_query(
                "test query", all_tables, limit=5
            )

            # Should return all tables as fallback
            assert len(result_tables) == 2
            assert result_tables == all_tables

    @patch("sq3m.application.services.table_search_service.EmbeddingService")
    @patch("sys.exit")
    @patch("builtins.print")
    def test_error_message_formatting(
        self, mock_print, mock_exit, mock_embedding_service_class
    ):
        """Test that error messages are properly formatted."""
        # Mock embedding service with specific error
        mock_embedding_service = Mock()
        mock_embedding_service_class.return_value = mock_embedding_service
        specific_error = EmbeddingServiceError(
            "OpenAI API error (status 429): Rate limit exceeded"
        )
        mock_embedding_service.generate_embeddings_batch.side_effect = specific_error

        service = TableSearchService(
            self.api_key, search_repository=self.mock_repository
        )

        test_table = self.create_test_table()
        service.store_table_summaries_with_embeddings([test_table])

        # Check that error message contains the specific error
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        critical_error_calls = [
            call for call in print_calls if "❌ Critical error:" in call
        ]
        assert len(critical_error_calls) > 0
        assert "Rate limit exceeded" in critical_error_calls[0]
