from __future__ import annotations

import os

from dotenv import load_dotenv

from sq3m.domain.entities.database import DatabaseType


class Settings:
    def __init__(self) -> None:
        load_dotenv()

    @property
    def openai_api_key(self) -> str | None:
        return os.getenv("OPENAI_API_KEY")

    @property
    def openai_model(self) -> str:
        return os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    @property
    def db_host(self) -> str | None:
        return os.getenv("DB_HOST")

    @property
    def db_port(self) -> int | None:
        port_str = os.getenv("DB_PORT")
        if port_str:
            try:
                return int(port_str)
            except ValueError:
                return None
        return None

    @property
    def db_name(self) -> str | None:
        return os.getenv("DB_NAME")

    @property
    def db_username(self) -> str | None:
        return os.getenv("DB_USERNAME")

    @property
    def db_password(self) -> str | None:
        return os.getenv("DB_PASSWORD")

    @property
    def db_type(self) -> DatabaseType | None:
        db_type_str = os.getenv("DB_TYPE", "").lower()
        if db_type_str == "mysql":
            return DatabaseType.MYSQL
        elif db_type_str == "postgresql":
            return DatabaseType.POSTGRESQL
        return None

    def validate_openai_config(self) -> bool:
        return self.openai_api_key is not None

    def validate_db_config(self) -> bool:
        return all(
            [
                self.db_host,
                self.db_port,
                self.db_name,
                self.db_username,
                self.db_password,
                self.db_type,
            ]
        )
