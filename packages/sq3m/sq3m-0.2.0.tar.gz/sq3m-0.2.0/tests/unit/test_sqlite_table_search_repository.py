"""Tests for SQLite table search repository."""

from __future__ import annotations

import json
import sqlite3
import tempfile
from pathlib import Path

from sq3m.domain.entities.table_summary import SearchResult, TableSummary
from sq3m.infrastructure.database.sqlite_table_search_repository import (
    SQLiteTableSearchRepository,
)


class TestSQLiteTableSearchRepository:
    """Test cases for SQLiteTableSearchRepository."""

    def setup_method(self):
        """Set up test fixtures with temporary database."""
        import os

        fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)  # Close the file descriptor immediately
        self.repository = SQLiteTableSearchRepository(self.db_path)

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.repository.connection:
            self.repository.connection.close()
        Path(self.db_path).unlink(missing_ok=True)

    def test_initialization(self):
        """Test repository initialization."""
        assert self.repository.db_path == self.db_path
        assert self.repository.connection is None

    def test_get_connection(self):
        """Test database connection creation."""
        conn = self.repository._get_connection()

        assert conn is not None
        assert isinstance(conn, sqlite3.Connection)
        assert self.repository.connection is conn

    def test_initialize_storage(self):
        """Test storage initialization creates tables and triggers."""
        self.repository.initialize_storage()

        conn = self.repository._get_connection()
        cursor = conn.cursor()

        # Check main table exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='table_summaries'
        """)
        assert cursor.fetchone() is not None

        # Check FTS table exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='table_summaries_fts'
        """)
        assert cursor.fetchone() is not None

    def test_store_table_summary(self):
        """Test storing a single table summary."""
        self.repository.initialize_storage()

        embedding = [0.1, 0.2, 0.3]
        summary = TableSummary(
            table_name="users",
            summary="Users table with user information",
            purpose="Store user data",
            embedding=embedding,
        )

        self.repository.store_table_summary(summary)

        # Verify storage
        conn = self.repository._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM table_summaries WHERE table_name = ?", ("users",))
        row = cursor.fetchone()

        assert row is not None
        assert row["table_name"] == "users"
        assert row["summary"] == "Users table with user information"
        assert row["purpose"] == "Store user data"
        assert json.loads(row["embedding"]) == embedding

    def test_store_table_summary_without_embedding(self):
        """Test storing table summary without embedding."""
        self.repository.initialize_storage()

        summary = TableSummary(table_name="logs", summary="Application logs")

        self.repository.store_table_summary(summary)

        conn = self.repository._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM table_summaries WHERE table_name = ?", ("logs",))
        row = cursor.fetchone()

        assert row is not None
        assert row["embedding"] is None

    def test_store_table_summaries_batch(self):
        """Test storing multiple table summaries."""
        self.repository.initialize_storage()

        summaries = [
            TableSummary("users", "Users table", "Store users", [0.1, 0.2]),
            TableSummary("orders", "Orders table", "Store orders", [0.3, 0.4]),
            TableSummary("products", "Products table", "Store products", [0.5, 0.6]),
        ]

        self.repository.store_table_summaries(summaries)

        # Verify all are stored
        conn = self.repository._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM table_summaries")
        count = cursor.fetchone()["count"]

        assert count == 3

    def test_cosine_similarity_calculation(self):
        """Test cosine similarity calculation."""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        similarity = self.repository._cosine_similarity(vec1, vec2)
        assert abs(similarity - 1.0) < 0.001

        vec3 = [1.0, 0.0, 0.0]
        vec4 = [0.0, 1.0, 0.0]
        similarity = self.repository._cosine_similarity(vec3, vec4)
        assert abs(similarity - 0.0) < 0.001

    def test_cosine_similarity_edge_cases(self):
        """Test cosine similarity edge cases."""
        # Empty vectors
        assert self.repository._cosine_similarity([], []) == 0.0

        # Different lengths
        assert self.repository._cosine_similarity([1, 2], [1]) == 0.0

        # Zero magnitude
        assert self.repository._cosine_similarity([0, 0], [1, 1]) == 0.0

    def test_search_tables_vector(self):
        """Test vector-only search."""
        self.repository.initialize_storage()

        # Store test data
        summaries = [
            TableSummary("users", "User information", embedding=[1.0, 0.0, 0.0]),
            TableSummary("orders", "Order data", embedding=[0.5, 0.5, 0.0]),
            TableSummary("products", "Product catalog", embedding=[0.0, 1.0, 0.0]),
        ]
        self.repository.store_table_summaries(summaries)

        # Search with query similar to users table
        query_embedding = [0.9, 0.1, 0.0]
        results = self.repository.search_tables_vector(query_embedding, limit=2)

        assert len(results) == 2
        assert results[0].table_summary.table_name == "users"  # Most similar
        assert results[0].search_type == "vector"
        assert results[0].score > results[1].score

    def test_search_tables_keyword(self):
        """Test keyword-only search."""
        self.repository.initialize_storage()

        # Store test data
        summaries = [
            TableSummary("users", "User account information"),
            TableSummary("user_profiles", "User profile details"),
            TableSummary("orders", "Order transaction data"),
        ]
        self.repository.store_table_summaries(summaries)

        # Search for "user"
        results = self.repository.search_tables_keyword("user", limit=3)

        # Should find tables with "user" in summary
        assert len(results) >= 2
        for result in results[:2]:
            assert "user" in result.table_summary.summary.lower()
            assert result.search_type == "keyword"

    def test_search_tables_hybrid(self):
        """Test hybrid search combining vector and keyword."""
        self.repository.initialize_storage()

        # Store test data
        summaries = [
            TableSummary("users", "User information", embedding=[1.0, 0.0]),
            TableSummary("accounts", "Account data", embedding=[0.8, 0.2]),
            TableSummary("orders", "Order information", embedding=[0.0, 1.0]),
        ]
        self.repository.store_table_summaries(summaries)

        query_embedding = [0.9, 0.1]
        results = self.repository.search_tables_hybrid(
            "user information", query_embedding, limit=2
        )

        assert len(results) <= 2
        for result in results:
            assert result.search_type == "hybrid"
            assert isinstance(result.score, float)

    def test_reciprocal_rank_fusion(self):
        """Test RRF algorithm implementation."""
        # Create mock results
        vector_results = [
            SearchResult(TableSummary("table1", "summary1"), 0.9, "vector"),
            SearchResult(TableSummary("table2", "summary2"), 0.7, "vector"),
        ]

        keyword_results = [
            SearchResult(TableSummary("table2", "summary2"), 0.8, "keyword"),
            SearchResult(TableSummary("table3", "summary3"), 0.6, "keyword"),
        ]

        combined = self.repository._reciprocal_rank_fusion(
            vector_results, keyword_results, 0.7, 0.3
        )

        assert len(combined) == 3  # table1, table2, table3

        # table2 should rank highest (appears in both results)
        table2_result = next(
            r for r in combined if r.table_summary.table_name == "table2"
        )
        assert table2_result.search_type == "hybrid"

    def test_get_all_table_summaries(self):
        """Test retrieving all stored summaries."""
        self.repository.initialize_storage()

        summaries = [
            TableSummary("users", "Users", embedding=[0.1, 0.2]),
            TableSummary("orders", "Orders", embedding=[0.3, 0.4]),
        ]
        self.repository.store_table_summaries(summaries)

        all_summaries = self.repository.get_all_table_summaries()

        assert len(all_summaries) == 2
        table_names = {s.table_name for s in all_summaries}
        assert table_names == {"users", "orders"}

    def test_clear_table_summaries(self):
        """Test clearing all stored summaries."""
        self.repository.initialize_storage()

        # Store some data
        summary = TableSummary("test", "test summary")
        self.repository.store_table_summary(summary)

        # Verify data exists
        all_summaries = self.repository.get_all_table_summaries()
        assert len(all_summaries) == 1

        # Clear and verify
        self.repository.clear_table_summaries()
        all_summaries = self.repository.get_all_table_summaries()
        assert len(all_summaries) == 0

    def test_malformed_embedding_handling(self):
        """Test handling of malformed embedding data."""
        self.repository.initialize_storage()

        # Manually insert malformed data
        conn = self.repository._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO table_summaries (table_name, summary, embedding)
            VALUES (?, ?, ?)
        """,
            ("bad_table", "summary", "invalid_json"),
        )
        conn.commit()

        # Should handle gracefully without crashing
        results = self.repository.search_tables_vector([0.1, 0.2], limit=5)
        assert len(results) == 0  # No valid embeddings to search

    def test_search_with_no_stored_data(self):
        """Test search operations with empty database."""
        self.repository.initialize_storage()

        # Vector search
        vector_results = self.repository.search_tables_vector([0.1, 0.2], limit=5)
        assert len(vector_results) == 0

        # Keyword search
        keyword_results = self.repository.search_tables_keyword("test", limit=5)
        assert len(keyword_results) == 0

        # Hybrid search
        hybrid_results = self.repository.search_tables_hybrid(
            "test", [0.1, 0.2], limit=5
        )
        assert len(hybrid_results) == 0

    def test_sanitize_fts5_query(self):
        """Test FTS5 query sanitization."""
        self.repository.initialize_storage()

        # Test cases with various problematic characters
        test_cases = [
            (
                "특정 encounter의 location, practitioner, department",
                '"특정" OR "encounter" OR "location" OR "practitioner" OR "department"',
            ),
            (
                'user\'s data with quotes "test"',
                '"user" OR "data" OR "with" OR "quotes" OR "test"',
            ),
            ("data,with,commas", '"data" OR "with" OR "commas"'),
            ("table-name:value", '"table" OR "name" OR "value"'),
            ("한글과 English mixed", '"한글과" OR "English" OR "mixed"'),
            ("123 numbers and text", '"numbers" OR "and" OR "text"'),
            ("!@#$%^&*()", ""),  # Should handle pure symbols
            ("", ""),  # Empty query
        ]

        for input_query, expected_pattern in test_cases:
            sanitized = self.repository._sanitize_fts5_query(input_query)

            if expected_pattern:
                # Check that it contains expected words with OR separator
                assert " OR " in sanitized or '"' in sanitized
                # Should not contain problematic characters
                assert "," not in sanitized
                assert "(" not in sanitized
                assert ")" not in sanitized
            else:
                # Empty or symbol-only queries might return empty or escaped version
                assert isinstance(sanitized, str)

    def test_fallback_keyword_search(self):
        """Test fallback keyword search with LIKE queries."""
        self.repository.initialize_storage()

        # Store test data
        summaries = [
            TableSummary(
                "encounter_history",
                "Stores encounter location and practitioner history",
            ),
            TableSummary(
                "patient_encounters", "Patient encounter data with departments"
            ),
            TableSummary("user_accounts", "User account information"),
            TableSummary("product_orders", "Product order details"),
        ]
        self.repository.store_table_summaries(summaries)

        # Test fallback search
        results = self.repository._fallback_keyword_search(
            "encounter location", limit=5
        )

        assert len(results) > 0
        assert any("encounter" in r.table_summary.table_name.lower() for r in results)

        for result in results:
            assert result.search_type == "keyword_fallback"
            assert result.score == 1.0
            assert isinstance(result.table_summary, TableSummary)

    def test_keyword_search_with_fts5_error(self):
        """Test keyword search handles FTS5 errors gracefully."""
        self.repository.initialize_storage()

        # Store test data
        summaries = [
            TableSummary("encounters", "Medical encounter data"),
            TableSummary("locations", "Location information"),
        ]
        self.repository.store_table_summaries(summaries)

        # Test with problematic query that would cause FTS5 error
        problematic_queries = [
            "특정 encounter의 location, practitioner, department의 이력",
            'query with "quotes" and, commas',
            "query with (parentheses) and special!@# characters",
            "한글쿼리,콤마포함",
        ]

        for query in problematic_queries:
            # Should not raise an exception
            results = self.repository.search_tables_keyword(query, limit=5)

            # Should return some results (either from FTS5 or fallback)
            assert isinstance(results, list)

            for result in results:
                assert isinstance(result, SearchResult)
                assert result.search_type in ["keyword", "keyword_fallback"]

    def test_hybrid_search_with_fts5_fallback(self):
        """Test hybrid search works even when FTS5 fails."""
        self.repository.initialize_storage()

        # Store test data
        summaries = [
            TableSummary(
                "encounter_locations",
                "Location data for encounters",
                embedding=[0.8, 0.2],
            ),
            TableSummary(
                "practitioner_info", "Practitioner information", embedding=[0.6, 0.4]
            ),
            TableSummary(
                "department_history", "Department history records", embedding=[0.4, 0.6]
            ),
        ]
        self.repository.store_table_summaries(summaries)

        query = "특정 encounter의 location, practitioner, department의 이력"
        query_embedding = [0.7, 0.3]

        # Should work despite FTS5 syntax issues
        results = self.repository.search_tables_hybrid(query, query_embedding, limit=3)

        assert len(results) > 0
        assert len(results) <= 3

        for result in results:
            assert result.search_type == "hybrid"
            assert isinstance(result.score, float)
            assert result.score > 0

    def test_empty_keyword_fallback_search(self):
        """Test fallback search with queries that have no extractable keywords."""
        self.repository.initialize_storage()

        # Store some data
        summary = TableSummary("test_table", "Test data")
        self.repository.store_table_summary(summary)

        # Query with no extractable keywords
        results = self.repository._fallback_keyword_search("!@#$%^&*()", limit=5)

        # Should return empty results
        assert len(results) == 0

    def test_keyword_search_case_insensitive(self):
        """Test that fallback keyword search is case insensitive."""
        self.repository.initialize_storage()

        # Store test data
        summaries = [
            TableSummary("ENCOUNTERS", "Medical encounter data"),
            TableSummary("encounter_history", "Historical encounter records"),
        ]
        self.repository.store_table_summaries(summaries)

        # Test with different cases
        test_queries = ["encounter", "ENCOUNTER", "Encounter", "eNcOuNtEr"]

        for query in test_queries:
            results = self.repository._fallback_keyword_search(query, limit=5)

            # Should find both tables regardless of case
            assert len(results) >= 1

            # Check that we found encounter-related tables
            table_names = [r.table_summary.table_name.lower() for r in results]
            assert any("encounter" in name for name in table_names)

    def test_fts5_query_word_extraction(self):
        """Test that query sanitization properly extracts meaningful words."""
        self.repository.initialize_storage()

        test_cases = [
            # Korean and English mixed
            ("환자 encounter 정보", ["환자", "encounter", "정보"]),
            # English with numbers
            ("user123 data table", ["user", "data", "table"]),
            # Korean only
            ("사용자 테이블 정보", ["사용자", "테이블", "정보"]),
            # With special characters
            ("user-table_data@info.com", ["user", "table", "data", "info", "com"]),
        ]

        for query, expected_words in test_cases:
            sanitized = self.repository._sanitize_fts5_query(query)

            # Check that all expected words are in the sanitized query
            for word in expected_words:
                assert word in sanitized

    def test_large_query_word_limit(self):
        """Test that query sanitization limits the number of words."""
        self.repository.initialize_storage()

        # Create a query with many words
        long_query = " ".join([f"word{i}" for i in range(20)])  # 20 words

        sanitized = self.repository._sanitize_fts5_query(long_query)

        # Should limit to 10 words as per implementation
        word_count = sanitized.count(" OR ") + 1 if sanitized else 0
        assert word_count <= 10

    def test_connection_cleanup(self):
        """Test connection cleanup on object destruction."""
        # Create repository and get connection
        repo = SQLiteTableSearchRepository(self.db_path)
        _ = repo._get_connection()

        # Manually call __del__ to test cleanup
        repo.__del__()

        # Connection should be closed (this test mainly ensures no exceptions)
