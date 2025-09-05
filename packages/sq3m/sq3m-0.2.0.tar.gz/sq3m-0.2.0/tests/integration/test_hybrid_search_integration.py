"""Integration tests for hybrid search functionality."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from sq3m.application.services.table_search_service import TableSearchService
from sq3m.domain.entities.database import Column, Table
from sq3m.domain.entities.table_summary import TableSummary
from sq3m.infrastructure.database.sqlite_table_search_repository import (
    SQLiteTableSearchRepository,
)


class TestHybridSearchIntegration:
    """Integration tests for the complete hybrid search pipeline."""

    def setup_method(self):
        """Set up test fixtures with real SQLite database."""
        import os

        fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)  # Close the file descriptor immediately
        self.api_key = "test-api-key"

    def teardown_method(self):
        """Clean up test fixtures."""
        Path(self.db_path).unlink(missing_ok=True)

    @patch("sq3m.infrastructure.llm.embedding_service.OpenAI")
    def test_end_to_end_table_storage_and_search(self, mock_openai):
        """Test complete workflow from table storage to search."""
        # Mock OpenAI responses
        mock_client = Mock()
        mock_openai.return_value = mock_client

        # Mock embedding responses
        mock_client.embeddings.create.side_effect = [
            # Batch embeddings for storage
            Mock(
                data=[
                    Mock(embedding=[1.0, 0.0, 0.0]),  # users - strong user signal
                    Mock(embedding=[0.8, 0.2, 0.0]),  # user_profiles - related to users
                    Mock(embedding=[0.0, 1.0, 0.0]),  # orders - different domain
                    Mock(embedding=[0.0, 0.8, 0.2]),  # products - different domain
                ]
            ),
            # Query embedding
            Mock(data=[Mock(embedding=[0.9, 0.1, 0.0])]),  # Similar to users
        ]

        # Create test tables
        tables = [
            Table(
                name="users",
                columns=[
                    Column("id", "int", False, True),
                    Column("name", "varchar", False, False),
                    Column("email", "varchar", False, False),
                ],
                indexes=[],
                purpose="Store user account information",
                comment="Main users table",
            ),
            Table(
                name="user_profiles",
                columns=[
                    Column("user_id", "int", False, True),
                    Column("bio", "text", True, False),
                ],
                indexes=[],
                purpose="Store additional user profile data",
                comment="Extended user information",
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
                comment="Order transactions",
            ),
            Table(
                name="products",
                columns=[
                    Column("id", "int", False, True),
                    Column("name", "varchar", False, False),
                    Column("price", "decimal", False, False),
                ],
                indexes=[],
                purpose="Store product catalog",
                comment="Available products",
            ),
        ]

        # Create service with real SQLite repository
        repository = SQLiteTableSearchRepository(self.db_path)
        service = TableSearchService(self.api_key, search_repository=repository)

        # Store table summaries with embeddings
        service.store_table_summaries_with_embeddings(tables)

        # Verify storage
        all_summaries = service.get_all_summaries()
        assert len(all_summaries) == 4

        # All summaries should have embeddings
        for summary in all_summaries:
            assert summary.embedding is not None
            assert len(summary.embedding) > 0

        # Perform search for user-related tables
        results = service.search_relevant_tables("user information", limit=2)

        # Should find user-related tables first
        assert len(results) == 2
        result_names = {r.table_summary.table_name for r in results}
        assert "users" in result_names or "user_profiles" in result_names

        # Results should be sorted by relevance
        assert results[0].score >= results[1].score

    @patch("sq3m.infrastructure.llm.embedding_service.OpenAI")
    def test_hybrid_search_vs_keyword_only(self, mock_openai):
        """Test that hybrid search provides better results than keyword-only."""
        # Mock OpenAI client
        mock_client = Mock()
        mock_openai.return_value = mock_client

        # Create embeddings that show semantic similarity
        mock_client.embeddings.create.side_effect = [
            # Storage embeddings
            Mock(
                data=[
                    Mock(
                        embedding=[1.0, 0.0, 0.0]
                    ),  # customers (semantically similar to users)
                    Mock(embedding=[0.0, 1.0, 0.0]),  # inventory (unrelated)
                    Mock(
                        embedding=[0.9, 0.1, 0.0]
                    ),  # accounts (somewhat similar to users)
                ]
            ),
            # Query embedding (similar to customers and accounts)
            Mock(data=[Mock(embedding=[0.95, 0.05, 0.0])]),
        ]

        repository = SQLiteTableSearchRepository(self.db_path)
        service = TableSearchService(self.api_key, search_repository=repository)

        # Create tables where keyword search would miss semantic similarity
        tables = [
            Table(
                name="customers",
                columns=[Column("id", "int", False, True)],
                indexes=[],
                purpose="Store customer information",  # No direct "user" keyword
                comment="Customer data storage",
            ),
            Table(
                name="inventory",
                columns=[Column("id", "int", False, True)],
                indexes=[],
                purpose="Track product inventory",
                comment="Stock management",
            ),
            Table(
                name="accounts",
                columns=[Column("id", "int", False, True)],
                indexes=[],
                purpose="Manage account details",  # Related to users but no "user" keyword
                comment="Account management",
            ),
        ]

        service.store_table_summaries_with_embeddings(tables)

        # Search for "user data" - no exact keyword matches
        hybrid_results = service.search_relevant_tables("user data", limit=3)

        # Hybrid search should find semantically related tables
        assert len(hybrid_results) > 0

        # Get keyword-only results for comparison
        keyword_results = repository.search_tables_keyword("user data", limit=3)

        # Hybrid should potentially find more relevant results than pure keyword
        # (This test validates the integration works, specific ranking depends on actual embeddings)
        assert len(hybrid_results) >= len(keyword_results)

    @patch("sq3m.infrastructure.llm.embedding_service.OpenAI")
    def test_search_with_table_filtering(self, mock_openai):
        """Test integration with table filtering for LLM prompts."""
        # Mock OpenAI client
        mock_client = Mock()
        mock_openai.return_value = mock_client

        # Create distinct embeddings
        mock_client.embeddings.create.side_effect = [
            # Storage embeddings - create clear semantic clusters
            Mock(
                data=[
                    Mock(
                        embedding=[1.0, 0.0, 0.0, 0.0]
                    ),  # user_accounts - user cluster
                    Mock(
                        embedding=[0.9, 0.1, 0.0, 0.0]
                    ),  # user_sessions - user cluster
                    Mock(
                        embedding=[0.8, 0.2, 0.0, 0.0]
                    ),  # user_preferences - user cluster
                    Mock(embedding=[0.0, 1.0, 0.0, 0.0]),  # orders - order cluster
                    Mock(embedding=[0.0, 0.9, 0.1, 0.0]),  # order_items - order cluster
                    Mock(embedding=[0.0, 0.0, 1.0, 0.0]),  # products - product cluster
                    Mock(
                        embedding=[0.0, 0.0, 0.9, 0.1]
                    ),  # categories - product cluster
                    Mock(embedding=[0.0, 0.0, 0.0, 1.0]),  # logs - unrelated
                ]
            ),
            # Query embedding - similar to user cluster
            Mock(data=[Mock(embedding=[0.95, 0.05, 0.0, 0.0])]),
        ]

        repository = SQLiteTableSearchRepository(self.db_path)
        service = TableSearchService(self.api_key, search_repository=repository)

        # Create many tables to test filtering
        tables = []
        table_names = [
            "user_accounts",
            "user_sessions",
            "user_preferences",
            "orders",
            "order_items",
            "products",
            "categories",
            "logs",
        ]

        tables = [
            Table(
                name=name,
                columns=[Column("id", "int", False, True)],
                indexes=[],
                purpose=f"Manages {name.replace('_', ' ')} data",
            )
            for name in table_names
        ]

        service.store_table_summaries_with_embeddings(tables)

        # Use get_tables_for_query which is the actual integration point
        relevant_tables = service.get_tables_for_query(
            "show user account information", tables, limit=3
        )

        # Should return only the most relevant tables
        assert len(relevant_tables) == 3

        # Should prioritize user-related tables
        table_names_result = {t.name for t in relevant_tables}
        user_related_count = sum(1 for name in table_names_result if "user" in name)

        # At least some of the top results should be user-related
        assert user_related_count > 0

    def test_repository_persistence(self):
        """Test that data persists between repository instances."""
        # Create and populate first repository instance
        repo1 = SQLiteTableSearchRepository(self.db_path)
        repo1.initialize_storage()

        summary = TableSummary(
            table_name="persistent_table",
            summary="This table should persist",
            embedding=[0.1, 0.2, 0.3, 0.4],
        )
        repo1.store_table_summary(summary)

        # Close first repository
        if repo1.connection:
            repo1.connection.close()

        # Create new repository instance
        repo2 = SQLiteTableSearchRepository(self.db_path)

        # Data should still be there
        all_summaries = repo2.get_all_table_summaries()
        assert len(all_summaries) == 1
        assert all_summaries[0].table_name == "persistent_table"
        assert all_summaries[0].embedding == [0.1, 0.2, 0.3, 0.4]

    @patch("sys.exit")
    def test_error_recovery_and_fallbacks(self, mock_exit):
        """Test system behavior when components fail."""
        repository = SQLiteTableSearchRepository(self.db_path)

        # Test with mock embedding service that fails
        with patch(
            "sq3m.application.services.table_search_service.EmbeddingService"
        ) as mock_service_class:
            mock_service = Mock()
            mock_service_class.return_value = mock_service

            # Make embedding generation fail during storage
            mock_service.generate_embeddings_batch.side_effect = Exception("API Error")

            service = TableSearchService(self.api_key, search_repository=repository)

            # Create test table
            table = Table(
                name="test_table",
                columns=[Column("id", "int", False, True)],
                indexes=[],
                purpose="Test table",
            )

            # Storage should call sys.exit when embeddings fail
            service.store_table_summaries_with_embeddings([table])

            # Verify sys.exit was called
            mock_exit.assert_called_once_with(1)

    @patch("sq3m.infrastructure.llm.embedding_service.OpenAI")
    def test_large_dataset_performance(self, mock_openai):
        """Test system behavior with larger number of tables."""
        # Mock OpenAI client with batch embeddings
        mock_client = Mock()
        mock_openai.return_value = mock_client

        # Generate embeddings for many tables
        num_tables = 50
        embeddings = [
            [i / num_tables, (i + 1) / num_tables, 0.1, 0.1] for i in range(num_tables)
        ]

        mock_client.embeddings.create.side_effect = [
            Mock(data=[Mock(embedding=emb) for emb in embeddings]),
            Mock(data=[Mock(embedding=[0.5, 0.5, 0.1, 0.1])]),  # Query embedding
        ]

        repository = SQLiteTableSearchRepository(self.db_path)
        service = TableSearchService(self.api_key, search_repository=repository)

        # Create many tables
        tables = [
            Table(
                name=f"table_{i:02d}",
                columns=[Column("id", "int", False, True)],
                indexes=[],
                purpose=f"Purpose for table {i}",
            )
            for i in range(num_tables)
        ]

        # Store all tables
        service.store_table_summaries_with_embeddings(tables)

        # Verify all were stored
        all_summaries = service.get_all_summaries()
        assert len(all_summaries) == num_tables

        # Search should still work efficiently
        results = service.search_relevant_tables("find relevant data", limit=10)
        assert len(results) <= 10

        # Results should be properly ranked
        for i in range(len(results) - 1):
            assert results[i].score >= results[i + 1].score
