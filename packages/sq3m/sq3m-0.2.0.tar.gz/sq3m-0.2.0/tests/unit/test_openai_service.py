from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from sq3m.domain.entities.database import SQLQuery, Table
from sq3m.infrastructure.llm.openai_service import OpenAIService


class TestOpenAIService:
    @pytest.fixture  # type: ignore[misc]
    def mock_openai_client(self) -> Mock:
        return Mock()

    @pytest.fixture  # type: ignore[misc]
    def openai_service(self, mock_openai_client: Mock) -> OpenAIService:
        with (
            patch("sq3m.infrastructure.llm.openai_service.OpenAI") as mock_openai,
            patch("sq3m.infrastructure.llm.openai_service.AsyncOpenAI"),
        ):
            mock_openai.return_value = mock_openai_client
            service = OpenAIService("test-api-key", "gpt-3.5-turbo")
            return service

    def test_openai_service_initialization(self) -> None:
        with (
            patch("sq3m.infrastructure.llm.openai_service.OpenAI") as mock_openai,
            patch("sq3m.infrastructure.llm.openai_service.AsyncOpenAI"),
        ):
            service = OpenAIService("test-api-key", "gpt-4")

            mock_openai.assert_called_once_with(api_key="test-api-key", base_url=None)
            assert service.model == "gpt-4"

    def test_openai_service_default_model(self) -> None:
        with (
            patch("sq3m.infrastructure.llm.openai_service.OpenAI"),
            patch("sq3m.infrastructure.llm.openai_service.AsyncOpenAI"),
        ):
            service = OpenAIService("test-api-key")
            assert service.model == "gpt-3.5-turbo"

    def test_infer_table_purpose_success(
        self,
        openai_service: OpenAIService,
        mock_openai_client: Mock,
        sample_table: Table,
    ) -> None:
        # Setup mock response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "This table stores user information"
        mock_openai_client.chat.completions.create.return_value = mock_response

        # Execute
        result = openai_service.infer_table_purpose(sample_table)

        # Assert
        assert result == "This table stores user information"
        mock_openai_client.chat.completions.create.assert_called_once()

        # Check call arguments
        call_args = mock_openai_client.chat.completions.create.call_args
        assert call_args[1]["model"] == "gpt-3.5-turbo"
        assert len(call_args[1]["messages"]) == 2

    def test_infer_table_purpose_with_exception(
        self,
        openai_service: OpenAIService,
        mock_openai_client: Mock,
        sample_table: Table,
    ) -> None:
        # Setup mock to raise exception
        mock_openai_client.chat.completions.create.side_effect = Exception("API Error")

        # Execute
        result = openai_service.infer_table_purpose(sample_table)

        # Assert
        assert (
            result is not None
            and "Could not infer purpose for table users: API Error" in result
        )

    def test_generate_sql_success_with_valid_json(
        self,
        openai_service: OpenAIService,
        mock_openai_client: Mock,
        sample_tables: list[Table],
    ) -> None:
        # Setup mock response with valid JSON
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """
        {
            "sql": "SELECT * FROM users",
            "explanation": "This query selects all users",
            "confidence": 90
        }
        """
        mock_openai_client.chat.completions.create.return_value = mock_response

        # Execute
        result = openai_service.generate_sql("Show all users", sample_tables)

        # Assert
        assert isinstance(result, SQLQuery)
        assert result.natural_language == "Show all users"
        assert result.sql == "SELECT * FROM users"
        assert result.explanation == "This query selects all users"
        assert result.confidence == 0.9  # Converted to 0-1 range

    def test_generate_sql_success_with_invalid_json(
        self,
        openai_service: OpenAIService,
        mock_openai_client: Mock,
        sample_tables: list[Table],
    ) -> None:
        # Setup mock response with invalid JSON
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "SELECT * FROM users"  # Not JSON
        mock_openai_client.chat.completions.create.return_value = mock_response

        # Execute
        result = openai_service.generate_sql("Show all users", sample_tables)

        # Assert
        assert isinstance(result, SQLQuery)
        assert result.natural_language == "Show all users"
        assert result.sql == "SELECT * FROM users"
        assert result.explanation == "Generated SQL query"
        assert result.confidence == 0.5

    def test_generate_sql_with_exception(
        self,
        openai_service: OpenAIService,
        mock_openai_client: Mock,
        sample_tables: list[Table],
    ) -> None:
        # Setup mock to raise exception
        mock_openai_client.chat.completions.create.side_effect = Exception("API Error")

        # Execute
        result = openai_service.generate_sql("Show all users", sample_tables)

        # Assert
        assert isinstance(result, SQLQuery)
        assert result.natural_language == "Show all users"
        assert (
            result.sql is not None
            and "-- Error generating SQL: API Error" in result.sql
        )
        assert (
            result.explanation is not None
            and "Failed to generate SQL: API Error" in result.explanation
        )
        assert result.confidence == 0.0

    def test_generate_sql_includes_table_information(
        self,
        openai_service: OpenAIService,
        mock_openai_client: Mock,
        sample_tables: list[Table],
    ) -> None:
        # Setup mock response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[
            0
        ].message.content = (
            '{"sql": "SELECT * FROM users", "explanation": "test", "confidence": 85}'
        )
        mock_openai_client.chat.completions.create.return_value = mock_response

        # Execute
        openai_service.generate_sql("Show all users", sample_tables)

        # Assert
        call_args = mock_openai_client.chat.completions.create.call_args
        prompt_content = call_args[1]["messages"][1]["content"]

        # Check that table information is included in the prompt
        assert "Table: users" in prompt_content
        assert "Table: products" in prompt_content
        assert "Purpose:" in prompt_content  # Should include table purposes
        assert "Columns (" in prompt_content  # Should include column information

    def test_generate_sql_parameters(
        self,
        openai_service: OpenAIService,
        mock_openai_client: Mock,
        sample_tables: list[Table],
    ) -> None:
        # Setup mock response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"sql": "SELECT * FROM users"}'
        mock_openai_client.chat.completions.create.return_value = mock_response

        # Execute
        openai_service.generate_sql("Show all users", sample_tables)

        # Assert call parameters
        call_args = mock_openai_client.chat.completions.create.call_args
        assert call_args[1]["model"] == "gpt-3.5-turbo"
        assert len(call_args[1]["messages"]) == 2
        assert call_args[1]["messages"][0]["role"] == "system"
        assert call_args[1]["messages"][1]["role"] == "user"

    def test_generate_sql_with_error_feedback_success(
        self,
        openai_service: OpenAIService,
        mock_openai_client: Mock,
        sample_tables: list[Table],
    ) -> None:
        # Setup mock response with corrected JSON
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """
        {
            "sql": "SELECT id, name FROM users",
            "explanation": "The error was caused by referencing non-existent column 'email'. I fixed it by selecting only existing columns.",
            "confidence": 88
        }
        """
        mock_openai_client.chat.completions.create.return_value = mock_response

        # Execute
        result = openai_service.generate_sql_with_error_feedback(
            "Show user info",
            sample_tables,
            "SELECT id, email FROM users",
            "Column 'email' doesn't exist",
        )

        # Assert
        assert isinstance(result, SQLQuery)
        assert result.natural_language == "Show user info"
        assert result.sql == "SELECT id, name FROM users"
        assert (
            result.explanation is not None
            and "non-existent column" in result.explanation
        )
        assert result.confidence == 0.88

        # Verify call was made with correct parameters
        call_args = mock_openai_client.chat.completions.create.call_args
        assert call_args[1]["model"] == "gpt-3.5-turbo"

        # Check that error feedback is included in prompt
        prompt_content = call_args[1]["messages"][1]["content"]
        assert "PREVIOUS SQL QUERY (FAILED)" in prompt_content
        assert "SELECT id, email FROM users" in prompt_content
        assert "Column 'email' doesn't exist" in prompt_content

    def test_generate_sql_with_error_feedback_invalid_json(
        self,
        openai_service: OpenAIService,
        mock_openai_client: Mock,
        sample_tables: list[Table],
    ) -> None:
        # Setup mock response with invalid JSON
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[
            0
        ].message.content = "SELECT id, name FROM users"  # Not JSON
        mock_openai_client.chat.completions.create.return_value = mock_response

        # Execute
        result = openai_service.generate_sql_with_error_feedback(
            "Show users",
            sample_tables,
            "SELECT * FROM invalid_table",
            "Table doesn't exist",
        )

        # Assert
        assert isinstance(result, SQLQuery)
        assert result.natural_language == "Show users"
        assert result.sql == "SELECT id, name FROM users"
        assert result.explanation == "Corrected SQL query based on error feedback"
        assert result.confidence == 0.4

    def test_generate_sql_with_error_feedback_exception(
        self,
        openai_service: OpenAIService,
        mock_openai_client: Mock,
        sample_tables: list[Table],
    ) -> None:
        # Setup mock to raise exception
        mock_openai_client.chat.completions.create.side_effect = Exception("API Error")

        # Execute
        result = openai_service.generate_sql_with_error_feedback(
            "Show users", sample_tables, "SELECT * FROM users", "Syntax error"
        )

        # Assert
        assert isinstance(result, SQLQuery)
        assert result.natural_language == "Show users"
        assert (
            result.sql is not None
            and "-- Error generating corrected SQL: API Error" in result.sql
        )
        assert (
            result.explanation is not None
            and "Failed to generate corrected SQL: API Error" in result.explanation
        )
        assert result.confidence == 0.0
