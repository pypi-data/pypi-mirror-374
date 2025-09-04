from __future__ import annotations

import pytest

from sq3m.domain.entities.database import DatabaseConnection, DatabaseType
from sq3m.infrastructure.database.mysql_repository import MySQLRepository
from sq3m.infrastructure.database.postgresql_repository import PostgreSQLRepository


@pytest.mark.integration
class TestMySQLRepository:
    def test_mysql_repository_instantiation(self) -> None:
        repository = MySQLRepository()
        assert repository.connection is None
        assert repository.cursor is None

    def test_mysql_test_connection_invalid_credentials(self) -> None:
        repository = MySQLRepository()
        connection = DatabaseConnection(
            host="invalid_host",
            port=3306,
            database="invalid_db",
            username="invalid_user",
            password="invalid_password",
            database_type=DatabaseType.MYSQL,
        )

        # Should return False for invalid connection
        result = repository.test_connection(connection)
        assert result is False

    def test_mysql_connect_invalid_credentials(self) -> None:
        repository = MySQLRepository()
        connection = DatabaseConnection(
            host="invalid_host",
            port=3306,
            database="invalid_db",
            username="invalid_user",
            password="invalid_password",
            database_type=DatabaseType.MYSQL,
        )

        # Should raise exception for invalid connection
        with pytest.raises((ConnectionError, OSError)):
            repository.connect(connection)

    def test_mysql_disconnect_without_connection(self) -> None:
        repository = MySQLRepository()
        # Should not raise exception
        repository.disconnect()


@pytest.mark.integration
class TestPostgreSQLRepository:
    def test_postgresql_repository_instantiation(self) -> None:
        repository = PostgreSQLRepository()
        assert repository.connection is None
        assert repository.cursor is None

    def test_postgresql_test_connection_invalid_credentials(self) -> None:
        repository = PostgreSQLRepository()
        connection = DatabaseConnection(
            host="invalid_host",
            port=5432,
            database="invalid_db",
            username="invalid_user",
            password="invalid_password",
            database_type=DatabaseType.POSTGRESQL,
        )

        # Should return False for invalid connection
        result = repository.test_connection(connection)
        assert result is False

    def test_postgresql_connect_invalid_credentials(self) -> None:
        repository = PostgreSQLRepository()
        connection = DatabaseConnection(
            host="invalid_host",
            port=5432,
            database="invalid_db",
            username="invalid_user",
            password="invalid_password",
            database_type=DatabaseType.POSTGRESQL,
        )

        # Should raise exception for invalid connection
        with pytest.raises((ConnectionError, OSError)):
            repository.connect(connection)

    def test_postgresql_disconnect_without_connection(self) -> None:
        repository = PostgreSQLRepository()
        # Should not raise exception
        repository.disconnect()


# Note: These are basic integration tests that don't require actual database connections.
# For full integration testing with real databases, you would need to set up test databases
# and provide valid connection credentials through environment variables or test fixtures.


@pytest.mark.integration
@pytest.mark.slow
class TestDatabaseRepositoriesWithRealConnections:
    """
    These tests require real database connections and should be run only when
    appropriate test databases are available. They are marked as 'slow' so they
    can be excluded from regular test runs with: pytest -m "not slow"
    """

    @pytest.mark.skip(reason="Requires real MySQL database")  # type: ignore[misc]
    def test_mysql_full_workflow(self) -> None:
        # This test would require a real MySQL database
        # Connection details would come from environment variables
        pass

    @pytest.mark.skip(reason="Requires real PostgreSQL database")  # type: ignore[misc]
    def test_postgresql_full_workflow(self) -> None:
        # This test would require a real PostgreSQL database
        # Connection details would come from environment variables
        pass
