from __future__ import annotations

import pytest

from sq3m.domain.entities.database import (
    Column,
    DatabaseConnection,
    DatabaseSchema,
    DatabaseType,
    Index,
    SQLQuery,
    Table,
)


@pytest.fixture  # type: ignore[misc]
def sample_column() -> Column:
    return Column(
        name="id",
        data_type="int",
        is_nullable=False,
        is_primary_key=True,
        default_value=None,
        comment="Primary key",
    )


@pytest.fixture  # type: ignore[misc]
def sample_columns() -> list[Column]:
    return [
        Column(
            name="id",
            data_type="int",
            is_nullable=False,
            is_primary_key=True,
            comment="Primary key",
        ),
        Column(
            name="name",
            data_type="varchar",
            is_nullable=False,
            is_primary_key=False,
            comment="User name",
        ),
        Column(
            name="email",
            data_type="varchar",
            is_nullable=True,
            is_primary_key=False,
            comment="User email",
        ),
    ]


@pytest.fixture  # type: ignore[misc]
def sample_index() -> Index:
    return Index(
        name="idx_user_email", columns=["email"], is_unique=True, index_type="BTREE"
    )


@pytest.fixture  # type: ignore[misc]
def sample_indexes() -> list[Index]:
    return [
        Index(name="PRIMARY", columns=["id"], is_unique=True, index_type="BTREE"),
        Index(
            name="idx_user_email", columns=["email"], is_unique=True, index_type="BTREE"
        ),
        Index(
            name="idx_user_name", columns=["name"], is_unique=False, index_type="BTREE"
        ),
    ]


@pytest.fixture  # type: ignore[misc]
def sample_table(sample_columns: list[Column], sample_indexes: list[Index]) -> Table:
    return Table(
        name="users",
        columns=sample_columns,
        indexes=sample_indexes,
        comment="User information table",
        purpose="Stores user account information including names and email addresses",
    )


@pytest.fixture  # type: ignore[misc]
def sample_tables(sample_table: Table) -> list[Table]:
    products_table = Table(
        name="products",
        columns=[
            Column(
                name="id",
                data_type="int",
                is_nullable=False,
                is_primary_key=True,
                comment="Product ID",
            ),
            Column(
                name="name",
                data_type="varchar",
                is_nullable=False,
                is_primary_key=False,
                comment="Product name",
            ),
            Column(
                name="price",
                data_type="decimal",
                is_nullable=False,
                is_primary_key=False,
                comment="Product price",
            ),
        ],
        indexes=[
            Index(name="PRIMARY", columns=["id"], is_unique=True, index_type="BTREE")
        ],
        comment="Product catalog table",
        purpose="Stores product information including names and prices",
    )

    return [sample_table, products_table]


@pytest.fixture  # type: ignore[misc]
def sample_database_schema(sample_tables: list[Table]) -> DatabaseSchema:
    return DatabaseSchema(
        name="test_db", tables=sample_tables, database_type=DatabaseType.MYSQL
    )


@pytest.fixture  # type: ignore[misc]
def sample_database_connection() -> DatabaseConnection:
    return DatabaseConnection(
        host="localhost",
        port=3306,
        database="test_db",
        username="test_user",
        password="test_password",
        database_type=DatabaseType.MYSQL,
    )


@pytest.fixture  # type: ignore[misc]
def sample_sql_query() -> SQLQuery:
    return SQLQuery(
        natural_language="Show all users",
        sql="SELECT * FROM users",
        explanation="This query retrieves all user records from the users table",
        confidence=0.95,
    )


@pytest.fixture  # type: ignore[misc]
def postgresql_connection() -> DatabaseConnection:
    return DatabaseConnection(
        host="localhost",
        port=5432,
        database="test_db",
        username="test_user",
        password="test_password",
        database_type=DatabaseType.POSTGRESQL,
    )
