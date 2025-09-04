from __future__ import annotations

from sq3m.domain.entities.database import (
    Column,
    DatabaseConnection,
    DatabaseSchema,
    DatabaseType,
    Index,
    SQLQuery,
    Table,
)


class TestDatabaseType:
    def test_enum_values(self) -> None:
        assert DatabaseType.MYSQL.value == "mysql"
        assert DatabaseType.POSTGRESQL.value == "postgresql"


class TestColumn:
    def test_column_creation(self) -> None:
        column = Column(
            name="test_column",
            data_type="varchar",
            is_nullable=True,
            is_primary_key=False,
            default_value="default",
            comment="Test column",
        )

        assert column.name == "test_column"
        assert column.data_type == "varchar"
        assert column.is_nullable is True
        assert column.is_primary_key is False
        assert column.default_value == "default"
        assert column.comment == "Test column"

    def test_column_optional_fields(self) -> None:
        column = Column(
            name="simple_column",
            data_type="int",
            is_nullable=False,
            is_primary_key=True,
        )

        assert column.default_value is None
        assert column.comment is None


class TestIndex:
    def test_index_creation(self) -> None:
        index = Index(
            name="test_index",
            columns=["col1", "col2"],
            is_unique=True,
            index_type="BTREE",
        )

        assert index.name == "test_index"
        assert index.columns == ["col1", "col2"]
        assert index.is_unique is True
        assert index.index_type == "BTREE"

    def test_index_optional_fields(self) -> None:
        index = Index(
            name="simple_index",
            columns=["col1"],
            is_unique=False,
        )

        assert index.index_type is None


class TestTable:
    def test_table_creation(
        self, sample_columns: list[Column], sample_indexes: list[Index]
    ) -> None:
        table = Table(
            name="test_table",
            columns=sample_columns,
            indexes=sample_indexes,
            comment="Test table",
            purpose="Testing purposes",
        )

        assert table.name == "test_table"
        assert table.columns == sample_columns
        assert table.indexes == sample_indexes
        assert table.comment == "Test table"
        assert table.purpose == "Testing purposes"

    def test_table_optional_fields(
        self, sample_columns: list[Column], sample_indexes: list[Index]
    ) -> None:
        table = Table(
            name="simple_table",
            columns=sample_columns,
            indexes=sample_indexes,
        )

        assert table.comment is None
        assert table.purpose is None


class TestDatabaseSchema:
    def test_schema_creation(self, sample_tables: list[Table]) -> None:
        schema = DatabaseSchema(
            name="test_schema",
            tables=sample_tables,
            database_type=DatabaseType.MYSQL,
        )

        assert schema.name == "test_schema"
        assert schema.tables == sample_tables
        assert schema.database_type == DatabaseType.MYSQL


class TestDatabaseConnection:
    def test_connection_creation(self) -> None:
        connection = DatabaseConnection(
            host="localhost",
            port=3306,
            database="test_db",
            username="user",
            password="password",
            database_type=DatabaseType.MYSQL,
        )

        assert connection.host == "localhost"
        assert connection.port == 3306
        assert connection.database == "test_db"
        assert connection.username == "user"
        assert connection.password == "password"
        assert connection.database_type == DatabaseType.MYSQL


class TestSQLQuery:
    def test_sql_query_creation(self) -> None:
        query = SQLQuery(
            natural_language="Show all users",
            sql="SELECT * FROM users",
            explanation="Retrieves all user records",
            confidence=0.95,
        )

        assert query.natural_language == "Show all users"
        assert query.sql == "SELECT * FROM users"
        assert query.explanation == "Retrieves all user records"
        assert query.confidence == 0.95

    def test_sql_query_optional_fields(self) -> None:
        query = SQLQuery(
            natural_language="Simple query",
            sql="SELECT 1",
        )

        assert query.explanation is None
        assert query.confidence is None
