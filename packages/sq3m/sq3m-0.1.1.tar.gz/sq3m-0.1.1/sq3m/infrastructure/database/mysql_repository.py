from __future__ import annotations

from typing import Any

import pymysql

from sq3m.domain.entities.database import (
    Column,
    DatabaseConnection,
    DatabaseSchema,
    DatabaseType,
    Index,
    Table,
)
from sq3m.domain.interfaces.database_repository import DatabaseRepository


class MySQLRepository(DatabaseRepository):
    def __init__(self) -> None:
        self.connection: Any = None
        self.cursor: Any = None

    def connect(self, connection: DatabaseConnection) -> None:
        try:
            self.connection = pymysql.connect(
                host=connection.host,
                port=connection.port,
                user=connection.username,
                password=connection.password,
                database=connection.database,
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
            )
            self.cursor = self.connection.cursor()
        except Exception as exc:  # Normalize connection errors for tests/consumers
            raise ConnectionError(f"Failed to connect to MySQL: {exc}") from exc

    def disconnect(self) -> None:
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def test_connection(self, connection: DatabaseConnection) -> bool:
        try:
            test_conn = pymysql.connect(
                host=connection.host,
                port=connection.port,
                user=connection.username,
                password=connection.password,
                database=connection.database,
                charset="utf8mb4",
            )
            test_conn.close()
            return True
        except Exception:
            return False

    def get_schema(self) -> DatabaseSchema:
        tables = self.get_tables()
        return DatabaseSchema(
            name=self.connection.db.decode("utf-8"),
            tables=tables,
            database_type=DatabaseType.MYSQL,
        )

    def get_tables(self) -> list[Table]:
        tables = []

        # Get table names and comments
        self.cursor.execute(
            """
            SELECT TABLE_NAME, TABLE_COMMENT
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_TYPE = 'BASE TABLE'
        """
        )

        table_info = self.cursor.fetchall()

        for table_data in table_info:
            table_name = table_data["TABLE_NAME"]
            table_comment = (
                table_data["TABLE_COMMENT"] if table_data["TABLE_COMMENT"] else None
            )

            # Get columns
            columns = self._get_table_columns(table_name)

            # Get indexes
            indexes = self._get_table_indexes(table_name)

            table = Table(
                name=table_name, columns=columns, indexes=indexes, comment=table_comment
            )
            tables.append(table)

        return tables

    def _get_table_columns(self, table_name: str) -> list[Column]:
        self.cursor.execute(
            """
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_KEY,
                   COLUMN_DEFAULT, COLUMN_COMMENT
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
            ORDER BY ORDINAL_POSITION
        """,
            (table_name,),
        )

        columns = []
        for col_data in self.cursor.fetchall():
            column = Column(
                name=col_data["COLUMN_NAME"],
                data_type=col_data["DATA_TYPE"],
                is_nullable=col_data["IS_NULLABLE"] == "YES",
                is_primary_key=col_data["COLUMN_KEY"] == "PRI",
                default_value=col_data["COLUMN_DEFAULT"],
                comment=col_data["COLUMN_COMMENT"]
                if col_data["COLUMN_COMMENT"]
                else None,
            )
            columns.append(column)

        return columns

    def _get_table_indexes(self, table_name: str) -> list[Index]:
        self.cursor.execute(
            """
            SELECT INDEX_NAME, COLUMN_NAME, NON_UNIQUE, INDEX_TYPE
            FROM INFORMATION_SCHEMA.STATISTICS
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
            ORDER BY INDEX_NAME, SEQ_IN_INDEX
        """,
            (table_name,),
        )

        indexes_dict = {}
        for idx_data in self.cursor.fetchall():
            idx_name = idx_data["INDEX_NAME"]
            if idx_name not in indexes_dict:
                indexes_dict[idx_name] = {
                    "columns": [],
                    "is_unique": idx_data["NON_UNIQUE"] == 0,
                    "index_type": idx_data["INDEX_TYPE"],
                }
            indexes_dict[idx_name]["columns"].append(idx_data["COLUMN_NAME"])

        indexes = []
        for idx_name, idx_info in indexes_dict.items():
            index = Index(
                name=idx_name,
                columns=idx_info["columns"],
                is_unique=idx_info["is_unique"],
                index_type=idx_info["index_type"],
            )
            indexes.append(index)

        return indexes

    def execute_query(self, sql: str) -> list[dict[Any, Any]]:
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return list(result)

    def get_table_sample_rows(
        self, table_name: str, limit: int = 10
    ) -> list[dict[Any, Any]]:
        self.cursor.execute(f"SELECT * FROM `{table_name}` LIMIT %s", (limit,))
        result = self.cursor.fetchall()
        return list(result)
