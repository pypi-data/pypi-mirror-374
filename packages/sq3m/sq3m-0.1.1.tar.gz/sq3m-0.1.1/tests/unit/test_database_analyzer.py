from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import Mock

import pytest

from sq3m.application.use_cases.database_analyzer import DatabaseAnalyzer
from sq3m.domain.interfaces.database_repository import DatabaseRepository
from sq3m.domain.interfaces.llm_service import LLMService

if TYPE_CHECKING:
    from sq3m.domain.entities.database import DatabaseSchema


class TestDatabaseAnalyzer:
    @pytest.fixture  # type: ignore[misc]
    def mock_database_repository(self) -> Mock:
        return Mock(spec=DatabaseRepository)

    @pytest.fixture  # type: ignore[misc]
    def mock_llm_service(self) -> Mock:
        return Mock(spec=LLMService)

    @pytest.fixture  # type: ignore[misc]
    def analyzer(
        self, mock_database_repository: Mock, mock_llm_service: Mock
    ) -> DatabaseAnalyzer:
        return DatabaseAnalyzer(mock_database_repository, mock_llm_service)

    def test_analyze_schema(
        self,
        analyzer: DatabaseAnalyzer,
        mock_database_repository: Mock,
        mock_llm_service: Mock,
        sample_database_schema: DatabaseSchema,
    ) -> None:
        # Setup mocks
        mock_database_repository.get_schema.return_value = sample_database_schema
        mock_llm_service.infer_table_purpose.side_effect = [
            "User management table",
            "Product catalog table",
        ]

        # Execute
        result = analyzer.analyze_schema()

        # Assert
        assert result == sample_database_schema
        assert mock_database_repository.get_schema.call_count == 1
        assert mock_llm_service.infer_table_purpose.call_count == 2

        # Check that purposes were set
        assert result.tables[0].purpose == "User management table"
        assert result.tables[1].purpose == "Product catalog table"

        # Check internal state
        assert analyzer.table_purposes["users"] == "User management table"
        assert analyzer.table_purposes["products"] == "Product catalog table"

    def test_get_table_purposes(
        self,
        analyzer: DatabaseAnalyzer,
        mock_database_repository: Mock,
        mock_llm_service: Mock,
        sample_database_schema: DatabaseSchema,
    ) -> None:
        # Setup
        mock_database_repository.get_schema.return_value = sample_database_schema
        mock_llm_service.infer_table_purpose.side_effect = [
            "User management",
            "Product catalog",
        ]

        # Execute analysis first
        analyzer.analyze_schema()

        # Get purposes
        purposes = analyzer.get_table_purposes()

        # Assert
        assert purposes == {
            "users": "User management",
            "products": "Product catalog",
        }
        # Ensure it returns a copy
        assert purposes is not analyzer.table_purposes

    def test_get_tables_with_purposes(
        self,
        analyzer: DatabaseAnalyzer,
        mock_database_repository: Mock,
        mock_llm_service: Mock,
        sample_database_schema: DatabaseSchema,
    ) -> None:
        # Setup
        mock_database_repository.get_schema.return_value = sample_database_schema
        analyzer.table_purposes = {
            "users": "User management",
            "products": "Product catalog",
        }

        # Execute
        result = analyzer.get_tables_with_purposes()

        # Assert
        assert len(result) == 2
        assert result[0].name == "users"
        assert result[0].purpose == "User management"
        assert result[1].name == "products"
        assert result[1].purpose == "Product catalog"

    def test_get_tables_with_purposes_no_cached_purposes(
        self,
        analyzer: DatabaseAnalyzer,
        mock_database_repository: Mock,
        sample_database_schema: DatabaseSchema,
    ) -> None:
        # Setup
        mock_database_repository.get_schema.return_value = sample_database_schema

        # Execute
        result = analyzer.get_tables_with_purposes()

        # Assert - should return tables with their existing purposes from schema
        assert len(result) == 2
        assert (
            result[0].purpose
            == "Stores user account information including names and email addresses"
        )  # From fixture
        assert (
            result[1].purpose == "Stores product information including names and prices"
        )  # From fixture
