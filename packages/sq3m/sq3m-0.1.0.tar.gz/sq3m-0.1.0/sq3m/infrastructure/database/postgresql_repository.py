from __future__ import annotations

from typing import Any

import psycopg2
import psycopg2.extras

from sq3m.domain.entities.database import (
    Column,
    DatabaseConnection,
    DatabaseSchema,
    DatabaseType,
    Index,
    Table,
)
from sq3m.domain.interfaces.database_repository import DatabaseRepository


class PostgreSQLRepository(DatabaseRepository):
    def __init__(self) -> None:
        self.connection: Any = None
        self.cursor: Any = None

    def connect(self, connection: DatabaseConnection) -> None:
        try:
            self.connection = psycopg2.connect(
                host=connection.host,
                port=connection.port,
                user=connection.username,
                password=connection.password,
                database=connection.database,
            )
            self.cursor = self.connection.cursor(
                cursor_factory=psycopg2.extras.DictCursor
            )
        except Exception as exc:  # Normalize connection errors for tests/consumers
            raise ConnectionError(f"Failed to connect to PostgreSQL: {exc}") from exc

    def disconnect(self) -> None:
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def test_connection(self, connection: DatabaseConnection) -> bool:
        try:
            test_conn = psycopg2.connect(
                host=connection.host,
                port=connection.port,
                user=connection.username,
                password=connection.password,
                database=connection.database,
            )
            test_conn.close()
            return True
        except Exception:
            return False

    def get_schema(self) -> DatabaseSchema:
        tables = self.get_tables()
        return DatabaseSchema(
            name=self.connection.info.dbname,
            tables=tables,
            database_type=DatabaseType.POSTGRESQL,
        )

    def get_tables(self) -> list[Table]:
        tables = []

        # Get table names and comments
        self.cursor.execute(
            """
            SELECT
                t.table_name,
                obj_description(c.oid, 'pg_class') as table_comment
            FROM information_schema.tables t
            LEFT JOIN pg_class c ON c.relname = t.table_name
            WHERE t.table_schema = 'public'
            AND t.table_type = 'BASE TABLE'
            ORDER BY t.table_name
        """
        )

        table_info = self.cursor.fetchall()

        for table_data in table_info:
            table_name = table_data["table_name"]
            table_comment = table_data["table_comment"]

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
            SELECT
                c.column_name,
                c.data_type,
                c.is_nullable,
                c.column_default,
                CASE
                    WHEN pk.column_name IS NOT NULL THEN true
                    ELSE false
                END as is_primary_key,
                col_description(pgc.oid, c.ordinal_position) as column_comment
            FROM information_schema.columns c
            LEFT JOIN (
                SELECT ku.table_name, ku.column_name
                FROM information_schema.table_constraints tc
                INNER JOIN information_schema.key_column_usage ku
                    ON tc.constraint_name = ku.constraint_name
                WHERE tc.constraint_type = 'PRIMARY KEY'
            ) pk ON c.table_name = pk.table_name AND c.column_name = pk.column_name
            LEFT JOIN pg_class pgc ON pgc.relname = c.table_name
            WHERE c.table_schema = 'public' AND c.table_name = %s
            ORDER BY c.ordinal_position
        """,
            (table_name,),
        )

        columns = []
        for col_data in self.cursor.fetchall():
            column = Column(
                name=col_data["column_name"],
                data_type=col_data["data_type"],
                is_nullable=col_data["is_nullable"] == "YES",
                is_primary_key=col_data["is_primary_key"],
                default_value=col_data["column_default"],
                comment=col_data["column_comment"],
            )
            columns.append(column)

        return columns

    def _get_table_indexes(self, table_name: str) -> list[Index]:
        self.cursor.execute(
            """
            SELECT
                i.relname as index_name,
                array_agg(a.attname ORDER BY array_position(ix.indkey, a.attnum)) as columns,
                ix.indisunique as is_unique,
                am.amname as index_type
            FROM pg_class t
            JOIN pg_index ix ON t.oid = ix.indrelid
            JOIN pg_class i ON i.oid = ix.indexrelid
            JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
            JOIN pg_am am ON i.relam = am.oid
            WHERE t.relname = %s AND t.relkind = 'r'
            GROUP BY i.relname, ix.indisunique, am.amname
            ORDER BY i.relname
        """,
            (table_name,),
        )

        indexes = []
        for idx_data in self.cursor.fetchall():
            index = Index(
                name=idx_data["index_name"],
                columns=list(idx_data["columns"]),
                is_unique=idx_data["is_unique"],
                index_type=idx_data["index_type"],
            )
            indexes.append(index)

        return indexes

    def execute_query(self, sql: str) -> list[dict[str, Any]]:
        self.cursor.execute(sql)
        return [dict(row) for row in self.cursor.fetchall()]

    def get_table_sample_rows(
        self, table_name: str, limit: int = 10
    ) -> list[dict[str, Any]]:
        self.cursor.execute(f'SELECT * FROM "{table_name}" LIMIT %s', (limit,))
        return [dict(row) for row in self.cursor.fetchall()]
