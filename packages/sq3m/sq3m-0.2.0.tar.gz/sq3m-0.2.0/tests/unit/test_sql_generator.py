from __future__ import annotations

from unittest.mock import Mock

import pytest

from sq3m.application.use_cases.sql_generator import SQLGenerator
from sq3m.domain.entities.database import SQLQuery, Table
from sq3m.domain.interfaces.database_repository import DatabaseRepository
from sq3m.domain.interfaces.llm_service import LLMService


class TestSQLGenerator:
    @pytest.fixture  # type: ignore[misc]
    def mock_database_repository(self) -> Mock:
        return Mock(spec=DatabaseRepository)

    @pytest.fixture  # type: ignore[misc]
    def mock_llm_service(self) -> Mock:
        return Mock(spec=LLMService)

    @pytest.fixture  # type: ignore[misc]
    def sql_generator(
        self, mock_database_repository: Mock, mock_llm_service: Mock
    ) -> SQLGenerator:
        return SQLGenerator(mock_database_repository, mock_llm_service)

    def test_generate_sql(
        self,
        sql_generator: SQLGenerator,
        mock_llm_service: Mock,
        sample_tables: list[Table],
        sample_sql_query: SQLQuery,
    ) -> None:
        # Setup
        mock_llm_service.generate_sql.return_value = sample_sql_query

        # Execute
        result = sql_generator.generate_sql("Show all users", sample_tables)

        # Assert
        assert result == sample_sql_query
        # Updated to match new signature with conversation_history parameter
        mock_llm_service.generate_sql.assert_called_once_with(
            "Show all users",
            sample_tables,
            None,  # conversation_history is None when no history available
        )

    def test_execute_sql(
        self,
        sql_generator: SQLGenerator,
        mock_database_repository: Mock,
    ) -> None:
        # Setup
        expected_results = [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}]
        mock_database_repository.execute_query.return_value = expected_results

        # Execute
        result = sql_generator.execute_sql("SELECT * FROM users")

        # Assert
        assert result == expected_results
        mock_database_repository.execute_query.assert_called_once_with(
            "SELECT * FROM users"
        )

    def test_generate_and_execute_success(
        self,
        sql_generator: SQLGenerator,
        mock_database_repository: Mock,
        mock_llm_service: Mock,
        sample_tables: list[Table],
        sample_sql_query: SQLQuery,
    ) -> None:
        # Setup
        mock_llm_service.generate_sql.return_value = sample_sql_query
        expected_results = [{"id": 1, "name": "John"}]
        mock_database_repository.execute_query.return_value = expected_results

        # Execute
        sql_query, results = sql_generator.generate_and_execute(
            "Show all users", sample_tables
        )

        # Assert
        assert sql_query == sample_sql_query
        assert results == expected_results
        # Updated to match new signature with conversation_history parameter
        mock_llm_service.generate_sql.assert_called_once_with(
            "Show all users",
            sample_tables,
            None,  # conversation_history is None when no history available
        )
        mock_database_repository.execute_query.assert_called_once_with(
            "SELECT * FROM users"
        )

    def test_generate_and_execute_with_error_sql(
        self,
        sql_generator: SQLGenerator,
        mock_database_repository: Mock,
        mock_llm_service: Mock,
        sample_tables: list[Table],
    ) -> None:
        # Setup - SQL query with error comment
        error_query = SQLQuery(
            natural_language="Invalid query",
            sql="-- Error: Could not generate SQL",
            explanation="Failed to parse",
            confidence=0.0,
        )
        mock_llm_service.generate_sql.return_value = error_query

        # Execute
        sql_query, results = sql_generator.generate_and_execute(
            "Invalid query", sample_tables
        )

        # Assert
        assert sql_query == error_query
        assert results == []  # Should not execute error SQL
        mock_database_repository.execute_query.assert_not_called()

    def test_generate_and_execute_with_empty_sql(
        self,
        sql_generator: SQLGenerator,
        mock_database_repository: Mock,
        mock_llm_service: Mock,
        sample_tables: list[Table],
    ) -> None:
        # Setup - Empty SQL query
        empty_query = SQLQuery(
            natural_language="Empty query",
            sql="",
            explanation="No SQL generated",
            confidence=0.0,
        )
        mock_llm_service.generate_sql.return_value = empty_query

        # Execute
        sql_query, results = sql_generator.generate_and_execute(
            "Empty query", sample_tables
        )

        # Assert
        assert sql_query == empty_query
        assert results == []  # Should not execute empty SQL
        mock_database_repository.execute_query.assert_not_called()

    def test_generate_and_execute_with_database_exception(
        self,
        sql_generator: SQLGenerator,
        mock_database_repository: Mock,
        mock_llm_service: Mock,
        sample_tables: list[Table],
        sample_sql_query: SQLQuery,
    ) -> None:
        # Setup - First attempt fails, retries also fail
        mock_llm_service.generate_sql.return_value = sample_sql_query

        # Create a corrected query for retry attempts
        corrected_query = SQLQuery(
            natural_language="Show all users",
            sql="SELECT id, name FROM users",
            explanation="Corrected query",
            confidence=0.8,
        )
        mock_llm_service.generate_sql_with_error_feedback.return_value = corrected_query

        # All attempts fail
        mock_database_repository.execute_query.side_effect = Exception("Database error")

        # Execute
        sql_query, results = sql_generator.generate_and_execute(
            "Show all users", sample_tables
        )

        # Assert - Should have tried 3 times (1 initial + 2 retries)
        assert mock_database_repository.execute_query.call_count == 3
        assert "Query failed after 3 attempts" in str(results[0]["error"])
        assert mock_llm_service.generate_sql_with_error_feedback.call_count == 2

    def test_generate_and_execute_retry_success(
        self,
        sql_generator: SQLGenerator,
        mock_database_repository: Mock,
        mock_llm_service: Mock,
        sample_tables: list[Table],
        sample_sql_query: SQLQuery,
    ) -> None:
        # Setup - First attempt fails, second succeeds
        mock_llm_service.generate_sql.return_value = sample_sql_query

        corrected_query = SQLQuery(
            natural_language="Show all users",
            sql="SELECT id, name FROM users",
            explanation="Corrected query after error",
            confidence=0.9,
        )
        mock_llm_service.generate_sql_with_error_feedback.return_value = corrected_query

        # First call fails, second succeeds
        mock_database_repository.execute_query.side_effect = [
            Exception("Column 'invalid_col' doesn't exist"),
            [{"id": 1, "name": "John"}],
        ]

        # Execute
        sql_query, results = sql_generator.generate_and_execute(
            "Show all users", sample_tables
        )

        # Assert
        assert sql_query == corrected_query  # Should return the successful query
        assert results == [{"id": 1, "name": "John"}]
        assert mock_database_repository.execute_query.call_count == 2
        mock_llm_service.generate_sql_with_error_feedback.assert_called_once_with(
            "Show all users",
            sample_tables,
            "SELECT * FROM users",
            "Column 'invalid_col' doesn't exist",
        )

    def test_generate_and_execute_max_retries_parameter(
        self,
        sql_generator: SQLGenerator,
        mock_database_repository: Mock,
        mock_llm_service: Mock,
        sample_tables: list[Table],
        sample_sql_query: SQLQuery,
    ) -> None:
        # Setup
        mock_llm_service.generate_sql.return_value = sample_sql_query
        corrected_query = SQLQuery(
            natural_language="Show all users",
            sql="SELECT id, name FROM users",
            explanation="Corrected query",
            confidence=0.8,
        )
        mock_llm_service.generate_sql_with_error_feedback.return_value = corrected_query

        # All attempts fail
        mock_database_repository.execute_query.side_effect = Exception("Database error")

        # Execute with custom max_retries
        sql_query, results = sql_generator.generate_and_execute(
            "Show all users", sample_tables, max_retries=1
        )

        # Assert - Should have tried 2 times (1 initial + 1 retry)
        assert mock_database_repository.execute_query.call_count == 2
        assert "Query failed after 2 attempts" in str(results[0]["error"])
        assert mock_llm_service.generate_sql_with_error_feedback.call_count == 1

    def test_generate_and_execute_no_retries_on_invalid_sql(
        self,
        sql_generator: SQLGenerator,
        mock_database_repository: Mock,
        mock_llm_service: Mock,
        sample_tables: list[Table],
    ) -> None:
        # Setup - First attempt returns error SQL, should not retry
        error_query = SQLQuery(
            natural_language="Invalid query",
            sql="-- Error: Could not generate SQL",
            explanation="Failed to parse",
            confidence=0.0,
        )
        mock_llm_service.generate_sql.return_value = error_query

        # Execute
        sql_query, results = sql_generator.generate_and_execute(
            "Invalid query", sample_tables
        )

        # Assert
        assert sql_query == error_query
        assert results == []  # Should not execute error SQL
        mock_database_repository.execute_query.assert_not_called()
        mock_llm_service.generate_sql_with_error_feedback.assert_not_called()
