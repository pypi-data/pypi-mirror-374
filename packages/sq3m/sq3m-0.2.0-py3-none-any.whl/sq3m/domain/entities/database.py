from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class DatabaseType(Enum):
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"


@dataclass
class Column:
    name: str
    data_type: str
    is_nullable: bool
    is_primary_key: bool
    default_value: str | None = None
    comment: str | None = None


@dataclass
class Index:
    name: str
    columns: list[str]
    is_unique: bool
    index_type: str | None = None


@dataclass
class Table:
    name: str
    columns: list[Column]
    indexes: list[Index]
    comment: str | None = None
    purpose: str | None = None
    sample_rows: list[dict[str, Any]] | None = None


@dataclass
class DatabaseSchema:
    name: str
    tables: list[Table]
    database_type: DatabaseType


@dataclass
class DatabaseConnection:
    host: str
    port: int
    database: str
    username: str
    password: str
    database_type: DatabaseType


@dataclass
class SQLQuery:
    natural_language: str
    sql: str
    explanation: str | None = None
    confidence: float | None = None
