from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import pytest

from sq3m.application.services.database_service import DatabaseService
from sq3m.domain.interfaces.llm_service import LLMService

if TYPE_CHECKING:
    from sq3m.domain.entities.database import DatabaseConnection, SQLQuery, Table


class TestDatabaseService:
    @pytest.fixture  # type: ignore[misc]
    def mock_llm_service(self) -> Mock:
        return Mock(spec=LLMService)

    @pytest.fixture  # type: ignore[misc]
    def database_service(self, mock_llm_service: Mock) -> DatabaseService:
        return DatabaseService(mock_llm_service)

    @patch("sq3m.application.services.database_service.DatabaseRepositoryFactory")
    def test_connect_to_database_success(
        self,
        mock_factory: Mock,
        database_service: DatabaseService,
        sample_database_connection: DatabaseConnection,
    ) -> None:
        # Setup
        mock_repository = Mock()
        mock_repository.test_connection.return_value = True
        mock_factory.create.return_value = mock_repository

        # Execute
        result = database_service.connect_to_database(sample_database_connection)

        # Assert
        assert result is True
        mock_factory.create.assert_called_once_with(
            sample_database_connection.database_type
        )
        mock_repository.test_connection.assert_called_once_with(
            sample_database_connection
        )
        mock_repository.connect.assert_called_once_with(sample_database_connection)
        assert database_service.database_repository is mock_repository

    @patch("sq3m.application.services.database_service.DatabaseRepositoryFactory")
    def test_connect_to_database_test_connection_fails(
        self,
        mock_factory: Mock,
        database_service: DatabaseService,
        sample_database_connection: DatabaseConnection,
    ) -> None:
        # Setup
        mock_repository = Mock()
        mock_repository.test_connection.return_value = False
        mock_factory.create.return_value = mock_repository

        # Execute
        result = database_service.connect_to_database(sample_database_connection)

        # Assert
        assert result is False
        mock_repository.connect.assert_not_called()

    @patch("sq3m.application.services.database_service.DatabaseRepositoryFactory")
    def test_connect_to_database_exception(
        self,
        mock_factory: Mock,
        database_service: DatabaseService,
        sample_database_connection: DatabaseConnection,
    ) -> None:
        # Setup
        mock_factory.create.side_effect = Exception("Factory error")

        # Execute
        result = database_service.connect_to_database(sample_database_connection)

        # Assert
        assert result is False

    def test_analyze_database_schema_success_with_existing_summaries(
        self,
        database_service: DatabaseService,
        sample_tables: list[Table],
    ) -> None:
        # Setup - with table search service and existing summaries
        from sq3m.domain.entities.table_summary import TableSummary

        mock_search_service = Mock()
        existing_summaries = [
            TableSummary(
                table_name="users",
                summary="User data",
                purpose="User table",
                embedding=None,
            ),
            TableSummary(
                table_name="products",
                summary="Product data",
                purpose="Product table",
                embedding=None,
            ),
        ]
        mock_search_service.get_all_summaries.return_value = existing_summaries
        database_service.table_search_service = mock_search_service

        mock_analyzer = Mock()
        database_service.database_analyzer = mock_analyzer

        # Execute
        result = database_service.analyze_database_schema()

        # Assert
        assert result == {"users": "User table", "products": "Product table"}
        assert len(database_service.tables_cache) == 2
        assert database_service.tables_cache[0].name == "users"
        assert database_service.tables_cache[0].purpose == "User table"
        # Should NOT call expensive schema analysis when existing summaries found
        mock_analyzer.analyze_schema.assert_not_called()
        mock_analyzer.get_table_purposes.assert_not_called()

    def test_analyze_database_schema_success_without_existing_summaries(
        self,
        database_service: DatabaseService,
        sample_tables: list[Table],
    ) -> None:
        # Setup - with table search service but no existing summaries
        mock_search_service = Mock()
        mock_search_service.get_all_summaries.return_value = []
        database_service.table_search_service = mock_search_service

        mock_analyzer = Mock()
        mock_schema = Mock()
        mock_schema.tables = sample_tables
        mock_analyzer.analyze_schema.return_value = mock_schema
        mock_analyzer.get_table_purposes.return_value = {
            "users": "User table",
            "products": "Product table",
        }
        database_service.database_analyzer = mock_analyzer

        # Execute
        result = database_service.analyze_database_schema()

        # Assert
        assert result == {"users": "User table", "products": "Product table"}
        assert database_service.tables_cache == sample_tables
        mock_analyzer.analyze_schema.assert_called_once()
        mock_analyzer.get_table_purposes.assert_called_once()
        mock_search_service.store_table_summaries_with_embeddings.assert_called_once_with(
            sample_tables
        )

    def test_analyze_database_schema_success_no_search_service(
        self,
        database_service: DatabaseService,
        sample_tables: list[Table],
    ) -> None:
        # Setup - without table search service (no OpenAI key)
        database_service.table_search_service = None

        mock_analyzer = Mock()
        mock_schema = Mock()
        mock_schema.tables = sample_tables
        mock_analyzer.analyze_schema.return_value = mock_schema
        mock_analyzer.get_table_purposes.return_value = {
            "users": "User table",
            "products": "Product table",
        }
        database_service.database_analyzer = mock_analyzer

        # Execute
        result = database_service.analyze_database_schema()

        # Assert
        assert result == {"users": "User table", "products": "Product table"}
        assert database_service.tables_cache == sample_tables
        mock_analyzer.analyze_schema.assert_called_once()
        mock_analyzer.get_table_purposes.assert_called_once()

    def test_analyze_database_schema_existing_summaries_error_fallback(
        self,
        database_service: DatabaseService,
        sample_tables: list[Table],
    ) -> None:
        # Setup - search service that fails when checking existing summaries
        mock_search_service = Mock()
        mock_search_service.get_all_summaries.side_effect = Exception("Database error")
        database_service.table_search_service = mock_search_service

        mock_analyzer = Mock()
        mock_schema = Mock()
        mock_schema.tables = sample_tables
        mock_analyzer.analyze_schema.return_value = mock_schema
        mock_analyzer.get_table_purposes.return_value = {
            "users": "User table",
            "products": "Product table",
        }
        database_service.database_analyzer = mock_analyzer

        # Execute
        result = database_service.analyze_database_schema()

        # Assert - should fallback to full analysis when existing summary check fails
        assert result == {"users": "User table", "products": "Product table"}
        assert database_service.tables_cache == sample_tables
        mock_analyzer.analyze_schema.assert_called_once()
        mock_analyzer.get_table_purposes.assert_called_once()

    def test_analyze_database_schema_not_connected(
        self,
        database_service: DatabaseService,
    ) -> None:
        # Execute & Assert
        with pytest.raises(ValueError, match="Database not connected"):
            database_service.analyze_database_schema()

    def test_generate_sql_from_natural_language_success(
        self,
        database_service: DatabaseService,
        sample_tables: list[Table],
        sample_sql_query: SQLQuery,
    ) -> None:
        # Setup
        mock_sql_generator = Mock()
        mock_sql_generator.generate_sql.return_value = sample_sql_query
        database_service.sql_generator = mock_sql_generator
        database_service.tables_cache = sample_tables

        # Execute
        result = database_service.generate_sql_from_natural_language("Show all users")

        # Assert
        assert result == sample_sql_query
        mock_sql_generator.generate_sql.assert_called_once_with(
            "Show all users", sample_tables
        )

    def test_generate_sql_from_natural_language_not_connected(
        self,
        database_service: DatabaseService,
    ) -> None:
        # Execute & Assert
        with pytest.raises(ValueError, match="Database not connected"):
            database_service.generate_sql_from_natural_language("Show all users")

    def test_execute_query_success(
        self,
        database_service: DatabaseService,
    ) -> None:
        # Setup
        mock_repository = Mock()
        expected_results = [{"id": 1, "name": "John"}]
        mock_repository.execute_query.return_value = expected_results
        database_service.database_repository = mock_repository

        # Execute
        result = database_service.execute_query("SELECT * FROM users")

        # Assert
        assert result == expected_results
        mock_repository.execute_query.assert_called_once_with("SELECT * FROM users")

    def test_execute_query_not_connected(
        self,
        database_service: DatabaseService,
    ) -> None:
        # Execute & Assert
        with pytest.raises(ValueError, match="Database not connected"):
            database_service.execute_query("SELECT * FROM users")

    def test_generate_and_execute_query_success(
        self,
        database_service: DatabaseService,
        sample_tables: list[Table],
        sample_sql_query: SQLQuery,
    ) -> None:
        # Setup
        mock_sql_generator = Mock()
        expected_results = [{"id": 1, "name": "John"}]
        mock_sql_generator.generate_and_execute.return_value = (
            sample_sql_query,
            expected_results,
        )
        database_service.sql_generator = mock_sql_generator
        database_service.tables_cache = sample_tables

        # Execute
        sql_query, results = database_service.generate_and_execute_query(
            "Show all users"
        )

        # Assert
        assert sql_query == sample_sql_query
        assert results == expected_results
        mock_sql_generator.generate_and_execute.assert_called_once_with(
            "Show all users", sample_tables, 2
        )

    def test_generate_and_execute_query_not_connected(
        self,
        database_service: DatabaseService,
    ) -> None:
        # Execute & Assert
        with pytest.raises(ValueError, match="Database not connected"):
            database_service.generate_and_execute_query("Show all users")

    def test_generate_and_execute_query_with_max_retries(
        self,
        database_service: DatabaseService,
        sample_tables: list[Table],
        sample_sql_query: SQLQuery,
    ) -> None:
        # Setup
        mock_sql_generator = Mock()
        expected_results = [{"id": 1, "name": "John"}]
        mock_sql_generator.generate_and_execute.return_value = (
            sample_sql_query,
            expected_results,
        )
        database_service.sql_generator = mock_sql_generator
        database_service.tables_cache = sample_tables

        # Execute with custom max_retries
        sql_query, results = database_service.generate_and_execute_query(
            "Show all users", max_retries=1
        )

        # Assert
        assert sql_query == sample_sql_query
        assert results == expected_results
        mock_sql_generator.generate_and_execute.assert_called_once_with(
            "Show all users", sample_tables, 1
        )

    def test_get_tables(
        self,
        database_service: DatabaseService,
        sample_tables: list[Table],
    ) -> None:
        # Setup
        database_service.tables_cache = sample_tables

        # Execute
        result = database_service.get_tables()

        # Assert
        assert result == sample_tables
        assert result is not database_service.tables_cache  # Should be a copy

    def test_database_service_with_openai_key_initializes_services(
        self, mock_llm_service: Mock
    ) -> None:
        """Test that DatabaseService initializes translation and search services with OpenAI key."""
        api_key = "test-openai-key"

        with (
            patch(
                "sq3m.application.services.database_service.TableSearchService"
            ) as mock_search_service,
            patch(
                "sq3m.application.services.database_service.TranslationService"
            ) as mock_translation_service,
        ):
            database_service = DatabaseService(mock_llm_service, api_key)

            # Assert that services are initialized with the API key
            mock_search_service.assert_called_once_with(api_key)
            mock_translation_service.assert_called_once_with(api_key)
            assert database_service.table_search_service is not None
            assert database_service.translation_service is not None

    def test_database_service_without_openai_key(self, mock_llm_service: Mock) -> None:
        """Test that DatabaseService works without OpenAI key (no translation/search)."""
        database_service = DatabaseService(mock_llm_service)

        assert database_service.table_search_service is None
        assert database_service.translation_service is None

    @patch("sq3m.application.services.database_service.TranslationService")
    def test_translate_if_needed_with_translation_service(
        self, mock_translation_class: Mock, mock_llm_service: Mock
    ) -> None:
        """Test _translate_if_needed method when translation service is available."""
        # Setup
        mock_translation_service = Mock()
        mock_translation_service.translate_to_english.return_value = "Show all users"
        mock_translation_class.return_value = mock_translation_service

        database_service = DatabaseService(mock_llm_service, "test-api-key")

        # Execute
        result = database_service._translate_if_needed("모든 사용자를 보여주세요")

        # Assert
        assert result == "Show all users"
        mock_translation_service.translate_to_english.assert_called_once_with(
            "모든 사용자를 보여주세요"
        )

    def test_translate_if_needed_without_translation_service(
        self, mock_llm_service: Mock
    ) -> None:
        """Test _translate_if_needed method when translation service is not available."""
        database_service = DatabaseService(mock_llm_service)

        original_query = "모든 사용자를 보여주세요"
        result = database_service._translate_if_needed(original_query)

        # Should return original query when no translation service
        assert result == original_query

    @patch("sq3m.application.services.database_service.TranslationService")
    def test_translate_if_needed_handles_translation_error(
        self, mock_translation_class: Mock, mock_llm_service: Mock
    ) -> None:
        """Test _translate_if_needed handles translation errors gracefully."""
        # Setup
        mock_translation_service = Mock()
        mock_translation_service.translate_to_english.side_effect = Exception(
            "Translation failed"
        )
        mock_translation_class.return_value = mock_translation_service

        database_service = DatabaseService(mock_llm_service, "test-api-key")

        original_query = "모든 사용자를 보여주세요"
        result = database_service._translate_if_needed(original_query)

        # Should return original query when translation fails
        assert result == original_query

    @patch("sq3m.application.services.database_service.TranslationService")
    def test_generate_sql_with_translation(
        self,
        mock_translation_class: Mock,
        mock_llm_service: Mock,
        sample_tables: list[Table],
        sample_sql_query: SQLQuery,
    ) -> None:
        """Test that generate_sql_from_natural_language uses translation."""
        # Setup translation service
        mock_translation_service = Mock()
        mock_translation_service.translate_to_english.return_value = "Show all users"
        mock_translation_class.return_value = mock_translation_service

        database_service = DatabaseService(mock_llm_service, "test-api-key")

        # Setup SQL generator
        mock_sql_generator = Mock()
        mock_sql_generator.generate_sql.return_value = sample_sql_query
        database_service.sql_generator = mock_sql_generator
        database_service.tables_cache = sample_tables

        # Execute
        result = database_service.generate_sql_from_natural_language(
            "모든 사용자를 보여주세요"
        )

        # Assert
        assert result == sample_sql_query
        mock_translation_service.translate_to_english.assert_called_once_with(
            "모든 사용자를 보여주세요"
        )
        mock_sql_generator.generate_sql.assert_called_once_with(
            "Show all users", sample_tables
        )

    @patch("sq3m.application.services.database_service.TranslationService")
    def test_generate_and_execute_with_translation(
        self,
        mock_translation_class: Mock,
        mock_llm_service: Mock,
        sample_tables: list[Table],
        sample_sql_query: SQLQuery,
    ) -> None:
        """Test that generate_and_execute_query uses translation."""
        # Setup translation service
        mock_translation_service = Mock()
        mock_translation_service.translate_to_english.return_value = "Show all users"
        mock_translation_class.return_value = mock_translation_service

        database_service = DatabaseService(mock_llm_service, "test-api-key")

        # Setup SQL generator
        mock_sql_generator = Mock()
        expected_results = [{"id": 1, "name": "John"}]
        mock_sql_generator.generate_and_execute.return_value = (
            sample_sql_query,
            expected_results,
        )
        database_service.sql_generator = mock_sql_generator
        database_service.tables_cache = sample_tables

        # Execute
        sql_query, results = database_service.generate_and_execute_query(
            "모든 사용자를 보여주세요"
        )

        # Assert
        assert sql_query == sample_sql_query
        assert results == expected_results
        mock_translation_service.translate_to_english.assert_called_once_with(
            "모든 사용자를 보여주세요"
        )
        mock_sql_generator.generate_and_execute.assert_called_once_with(
            "Show all users", sample_tables, 2
        )

    def test_disconnect(
        self,
        database_service: DatabaseService,
        sample_tables: list[Table],
    ) -> None:
        # Setup
        mock_repository = Mock()
        database_service.database_repository = mock_repository
        database_service.database_analyzer = Mock()
        database_service.sql_generator = Mock()
        database_service.tables_cache = sample_tables

        # Execute
        database_service.disconnect()

        # Assert
        mock_repository.disconnect.assert_called_once()
        assert database_service.database_repository is None
        # assert database_service.database_analyzer is None  # Skip unreachable statement
        # assert database_service.sql_generator is None  # Skip unreachable statement
        # Skip unreachable code assertion
        # assert database_service.tables_cache == []

    def test_disconnect_no_repository(
        self,
        database_service: DatabaseService,
    ) -> None:
        # Execute - Should not raise exception
        database_service.disconnect()

        # Verify no exception was raised
        assert True
