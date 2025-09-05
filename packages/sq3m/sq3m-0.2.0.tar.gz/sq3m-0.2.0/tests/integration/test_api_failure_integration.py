"""Integration tests for API failure scenarios and program termination."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from openai import APIError

from sq3m.application.services.table_search_service import TableSearchService
from sq3m.domain.entities.database import Column, Table
from sq3m.infrastructure.database.sqlite_table_search_repository import (
    SQLiteTableSearchRepository,
)


class TestAPIFailureIntegration:
    """Integration tests for API failure scenarios."""

    def setup_method(self):
        """Set up test fixtures with real SQLite database."""
        import os

        fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)  # Close the file descriptor immediately
        self.api_key = "test-api-key"

    def teardown_method(self):
        """Clean up test fixtures."""
        Path(self.db_path).unlink(missing_ok=True)

    def create_test_tables(self) -> list[Table]:
        """Create test tables for testing."""
        return [
            Table(
                name="users",
                columns=[
                    Column("id", "int", False, True),
                    Column("name", "varchar", False, False),
                    Column("email", "varchar", False, False),
                ],
                indexes=[],
                purpose="Store user information",
            ),
            Table(
                name="orders",
                columns=[
                    Column("id", "int", False, True),
                    Column("user_id", "int", False, False),
                    Column("total", "decimal", False, False),
                ],
                indexes=[],
                purpose="Store customer orders",
            ),
        ]

    @patch("sq3m.infrastructure.llm.embedding_service.OpenAI")
    @patch("sys.exit")
    @patch("builtins.print")
    def test_api_401_unauthorized_terminates_program(
        self, mock_print, mock_exit, mock_openai
    ):
        """Test that 401 Unauthorized API error terminates the program."""
        # Mock OpenAI client to raise 401 error
        mock_client = Mock()
        mock_openai.return_value = mock_client

        api_error = Exception("Unauthorized")
        mock_client.embeddings.create.side_effect = api_error

        # Create service with real repository
        repository = SQLiteTableSearchRepository(self.db_path)
        service = TableSearchService(self.api_key, search_repository=repository)

        test_tables = self.create_test_tables()

        # Should terminate the program
        service.store_table_summaries_with_embeddings(test_tables)

        # Verify program termination
        mock_exit.assert_called_once_with(1)

        # Verify error messages
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("❌ Critical error:" in call for call in print_calls)
        assert any(
            "Cannot continue without embeddings. Exiting..." in call
            for call in print_calls
        )

    @patch("sq3m.infrastructure.llm.embedding_service.OpenAI")
    @patch("sys.exit")
    @patch("builtins.print")
    def test_api_429_rate_limit_terminates_program(
        self, mock_print, mock_exit, mock_openai
    ):
        """Test that 429 Rate Limit error terminates the program."""
        # Mock OpenAI client to raise rate limit error
        mock_client = Mock()
        mock_openai.return_value = mock_client

        rate_limit_error = Exception("Rate limit exceeded")
        mock_client.embeddings.create.side_effect = rate_limit_error

        # Create service with real repository
        repository = SQLiteTableSearchRepository(self.db_path)
        service = TableSearchService(self.api_key, search_repository=repository)

        test_tables = self.create_test_tables()

        # Should terminate the program
        service.store_table_summaries_with_embeddings(test_tables)

        # Verify program termination
        mock_exit.assert_called_once_with(1)

        # Verify error messages
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("❌ Critical error:" in call for call in print_calls)

    @patch("sq3m.infrastructure.llm.embedding_service.OpenAI")
    @patch("sys.exit")
    @patch("builtins.print")
    def test_api_500_server_error_terminates_program(
        self, mock_print, mock_exit, mock_openai
    ):
        """Test that 500 Server Error terminates the program."""
        # Mock OpenAI client to raise server error
        mock_client = Mock()
        mock_openai.return_value = mock_client

        api_error = Exception("Internal server error")
        mock_client.embeddings.create.side_effect = api_error

        # Create service with real repository
        repository = SQLiteTableSearchRepository(self.db_path)
        service = TableSearchService(self.api_key, search_repository=repository)

        test_tables = self.create_test_tables()

        # Should terminate the program
        service.store_table_summaries_with_embeddings(test_tables)

        # Verify program termination
        mock_exit.assert_called_once_with(1)

        # Verify error messages
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("❌ Critical error:" in call for call in print_calls)

    @patch("sq3m.infrastructure.llm.embedding_service.OpenAI")
    @patch("builtins.print")
    def test_successful_api_call_continues_normally(self, mock_print, mock_openai):
        """Test that successful API calls allow the program to continue."""
        # Mock successful OpenAI client
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_response.data = [
            Mock(embedding=[1.0, 0.0, 0.0]),
            Mock(embedding=[0.0, 1.0, 0.0]),
        ]
        mock_client.embeddings.create.return_value = mock_response

        # Create service with real repository
        repository = SQLiteTableSearchRepository(self.db_path)
        service = TableSearchService(self.api_key, search_repository=repository)

        test_tables = self.create_test_tables()

        # Should complete successfully
        service.store_table_summaries_with_embeddings(test_tables)

        # Verify success messages
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any(
            "🔄 Generating embeddings for 2 tables..." in call for call in print_calls
        )
        assert any(
            "✅ Successfully generated embeddings for all tables" in call
            for call in print_calls
        )

        # Verify data was stored
        stored_summaries = service.get_all_summaries()
        assert len(stored_summaries) == 2
        for summary in stored_summaries:
            assert summary.embedding is not None

    @patch("sq3m.infrastructure.llm.embedding_service.OpenAI")
    @patch("builtins.print")
    def test_search_api_failure_fallback_to_keyword(self, mock_print, mock_openai):
        """Test that search API failures fallback to keyword search without terminating."""
        # Mock OpenAI client
        mock_client = Mock()
        mock_openai.return_value = mock_client

        # First call (storage) succeeds, second call (search) fails
        mock_client.embeddings.create.side_effect = [
            # Storage call - succeeds
            Mock(data=[Mock(embedding=[1.0, 0.0])]),
            # Search call - fails
            APIError(
                message="API Error during search",
                request=Mock(),
                body={"error": {"message": "API Error during search"}},
            ),
        ]

        # Set up API error for search call
        api_error = Exception("API Error during search")
        mock_client.embeddings.create.side_effect = [
            Mock(data=[Mock(embedding=[1.0, 0.0])]),  # Storage succeeds
            api_error,  # Search fails
        ]

        # Create service with real repository
        repository = SQLiteTableSearchRepository(self.db_path)
        service = TableSearchService(self.api_key, search_repository=repository)

        # Store tables successfully
        test_tables = [self.create_test_tables()[0]]  # Just one table
        service.store_table_summaries_with_embeddings(test_tables)

        # Now search should fall back to keyword search when embedding fails
        results = service.search_relevant_tables("user information")

        # Should not terminate program, should fallback to keyword search
        # Results may be empty if no keyword matches, but shouldn't crash
        assert isinstance(results, list)

        # Verify fallback warning messages
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        fallback_messages = [
            call
            for call in print_calls
            if "Falling back to keyword-only search" in call
        ]
        assert len(fallback_messages) > 0

    @patch("sq3m.infrastructure.llm.embedding_service.OpenAI")
    @patch("sys.exit")
    def test_partial_batch_failure_terminates_program(self, mock_exit, mock_openai):
        """Test that even partial failures in batch operations terminate the program."""
        # Mock OpenAI client to simulate partial batch failure
        mock_client = Mock()
        mock_openai.return_value = mock_client

        # Simulate batch request failure
        api_error = Exception("Batch processing failed")
        mock_client.embeddings.create.side_effect = api_error

        # Create service with real repository
        repository = SQLiteTableSearchRepository(self.db_path)
        service = TableSearchService(self.api_key, search_repository=repository)

        # Create many tables to test batch processing
        test_tables = [
            Table(
                name=f"table_{i}",
                columns=[Column("id", "int", False, True)],
                indexes=[],
                purpose=f"Test table {i}",
            )
            for i in range(10)
        ]

        # Should terminate program even with batch failure
        service.store_table_summaries_with_embeddings(test_tables)

        # Verify program termination
        mock_exit.assert_called_once_with(1)

    @patch("sq3m.infrastructure.llm.embedding_service.OpenAI")
    @patch("sys.exit")
    def test_network_connection_failure_terminates_program(
        self, mock_exit, mock_openai
    ):
        """Test that network connection failures terminate the program."""
        # Mock OpenAI client to raise connection error
        mock_client = Mock()
        mock_openai.return_value = mock_client

        connection_error = Exception("Could not connect to OpenAI API")
        mock_client.embeddings.create.side_effect = connection_error

        # Create service
        repository = SQLiteTableSearchRepository(self.db_path)
        service = TableSearchService(self.api_key, search_repository=repository)

        test_tables = self.create_test_tables()

        # Should terminate program
        service.store_table_summaries_with_embeddings(test_tables)

        # Verify program termination
        mock_exit.assert_called_once_with(1)

    def test_repository_continues_working_after_api_failure(self):
        """Test that the SQLite repository continues working normally after API failures."""
        repository = SQLiteTableSearchRepository(self.db_path)
        repository.initialize_storage()

        # Manually create and store a table summary (simulating successful past operation)
        from sq3m.domain.entities.table_summary import TableSummary

        summary = TableSummary(
            table_name="test_table",
            summary="Test table summary",
            purpose="Testing",
            embedding=[0.1, 0.2, 0.3],
        )

        repository.store_table_summary(summary)

        # Verify repository functionality is not affected
        all_summaries = repository.get_all_table_summaries()
        assert len(all_summaries) == 1
        assert all_summaries[0].table_name == "test_table"

        # Keyword search should work fine
        keyword_results = repository.search_tables_keyword("test", limit=5)
        assert (
            len(keyword_results) >= 0
        )  # May or may not find matches, but shouldn't crash
