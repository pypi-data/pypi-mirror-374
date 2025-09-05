from __future__ import annotations

import pytest

from sq3m.domain.entities.database import DatabaseType
from sq3m.infrastructure.database.mysql_repository import MySQLRepository
from sq3m.infrastructure.database.postgresql_repository import PostgreSQLRepository
from sq3m.infrastructure.database.repository_factory import DatabaseRepositoryFactory


class TestDatabaseRepositoryFactory:
    def test_create_mysql_repository(self) -> None:
        repository = DatabaseRepositoryFactory.create(DatabaseType.MYSQL)
        assert isinstance(repository, MySQLRepository)

    def test_create_postgresql_repository(self) -> None:
        repository = DatabaseRepositoryFactory.create(DatabaseType.POSTGRESQL)
        assert isinstance(repository, PostgreSQLRepository)

    def test_create_unsupported_database_type(self) -> None:
        # Create a mock enum value that doesn't exist in the factory
        with pytest.raises(ValueError, match="Unsupported database type"):
            # This should raise ValueError since we don't support this type
            class FakeDatabaseType:
                def __init__(self, value: str) -> None:
                    self.value = value

                def __str__(self) -> str:
                    return self.value

            fake_type = FakeDatabaseType("fake_db")
            DatabaseRepositoryFactory.create(fake_type)  # type: ignore[arg-type]

    def test_factory_has_all_database_types(self) -> None:
        # Ensure factory supports all defined database types
        supported_types = set(DatabaseRepositoryFactory._repositories.keys())
        all_types = set(DatabaseType)

        assert supported_types == all_types, (
            "Factory doesn't support all database types"
        )

    def test_repositories_are_different_instances(self) -> None:
        repo1 = DatabaseRepositoryFactory.create(DatabaseType.MYSQL)
        repo2 = DatabaseRepositoryFactory.create(DatabaseType.MYSQL)

        assert repo1 is not repo2, "Factory should create new instances"
        assert type(repo1) is type(repo2), "Both should be same type"
