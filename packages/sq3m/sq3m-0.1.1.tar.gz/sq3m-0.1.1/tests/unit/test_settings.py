from __future__ import annotations

from unittest.mock import patch

import pytest

from sq3m.config.settings import Settings
from sq3m.domain.entities.database import DatabaseType


class TestSettings:
    @pytest.fixture  # type: ignore[misc]
    def settings(self) -> Settings:
        with patch("sq3m.config.settings.load_dotenv"):
            return Settings()

    @patch.dict("os.environ", {})
    def test_openai_api_key_not_set(self, settings: Settings) -> None:
        assert settings.openai_api_key is None

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-api-key"})
    def test_openai_api_key_set(self, settings: Settings) -> None:
        assert settings.openai_api_key == "test-api-key"

    @patch.dict("os.environ", {})
    def test_openai_model_default(self, settings: Settings) -> None:
        assert settings.openai_model == "gpt-3.5-turbo"

    @patch.dict("os.environ", {"OPENAI_MODEL": "gpt-4"})
    def test_openai_model_custom(self, settings: Settings) -> None:
        assert settings.openai_model == "gpt-4"

    @patch.dict("os.environ", {})
    def test_db_host_not_set(self, settings: Settings) -> None:
        assert settings.db_host is None

    @patch.dict("os.environ", {"DB_HOST": "localhost"})
    def test_db_host_set(self, settings: Settings) -> None:
        assert settings.db_host == "localhost"

    @patch.dict("os.environ", {})
    def test_db_port_not_set(self, settings: Settings) -> None:
        assert settings.db_port is None

    @patch.dict("os.environ", {"DB_PORT": "3306"})
    def test_db_port_set(self, settings: Settings) -> None:
        assert settings.db_port == 3306

    @patch.dict("os.environ", {"DB_PORT": "invalid"})
    def test_db_port_invalid(self, settings: Settings) -> None:
        assert settings.db_port is None

    @patch.dict("os.environ", {})
    def test_db_name_not_set(self, settings: Settings) -> None:
        assert settings.db_name is None

    @patch.dict("os.environ", {"DB_NAME": "test_db"})
    def test_db_name_set(self, settings: Settings) -> None:
        assert settings.db_name == "test_db"

    @patch.dict("os.environ", {})
    def test_db_username_not_set(self, settings: Settings) -> None:
        assert settings.db_username is None

    @patch.dict("os.environ", {"DB_USERNAME": "test_user"})
    def test_db_username_set(self, settings: Settings) -> None:
        assert settings.db_username == "test_user"

    @patch.dict("os.environ", {})
    def test_db_password_not_set(self, settings: Settings) -> None:
        assert settings.db_password is None

    @patch.dict("os.environ", {"DB_PASSWORD": "test_password"})
    def test_db_password_set(self, settings: Settings) -> None:
        assert settings.db_password == "test_password"

    @patch.dict("os.environ", {})
    def test_db_type_not_set(self, settings: Settings) -> None:
        assert settings.db_type is None

    @patch.dict("os.environ", {"DB_TYPE": "mysql"})
    def test_db_type_mysql(self, settings: Settings) -> None:
        assert settings.db_type == DatabaseType.MYSQL

    @patch.dict("os.environ", {"DB_TYPE": "MYSQL"})
    def test_db_type_mysql_uppercase(self, settings: Settings) -> None:
        assert settings.db_type == DatabaseType.MYSQL

    @patch.dict("os.environ", {"DB_TYPE": "postgresql"})
    def test_db_type_postgresql(self, settings: Settings) -> None:
        assert settings.db_type == DatabaseType.POSTGRESQL

    @patch.dict("os.environ", {"DB_TYPE": "invalid"})
    def test_db_type_invalid(self, settings: Settings) -> None:
        assert settings.db_type is None

    @patch.dict("os.environ", {})
    def test_validate_openai_config_false(self, settings: Settings) -> None:
        assert settings.validate_openai_config() is False

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-api-key"})
    def test_validate_openai_config_true(self, settings: Settings) -> None:
        assert settings.validate_openai_config() is True

    @patch.dict("os.environ", {})
    def test_validate_db_config_false(self, settings: Settings) -> None:
        assert settings.validate_db_config() is False

    @patch.dict(
        "os.environ",
        {
            "DB_HOST": "localhost",
            "DB_PORT": "3306",
            "DB_NAME": "test_db",
            "DB_USERNAME": "test_user",
            "DB_PASSWORD": "test_password",
            "DB_TYPE": "mysql",
        },
    )
    def test_validate_db_config_true(self, settings: Settings) -> None:
        assert settings.validate_db_config() is True

    @patch.dict(
        "os.environ",
        {
            "DB_HOST": "localhost",
            "DB_PORT": "3306",
            "DB_NAME": "test_db",
            "DB_USERNAME": "test_user",
            # Missing DB_PASSWORD
            "DB_TYPE": "mysql",
        },
    )
    def test_validate_db_config_missing_password(self, settings: Settings) -> None:
        assert settings.validate_db_config() is False

    @patch.dict(
        "os.environ",
        {
            "DB_HOST": "localhost",
            "DB_PORT": "invalid",  # Invalid port
            "DB_NAME": "test_db",
            "DB_USERNAME": "test_user",
            "DB_PASSWORD": "test_password",
            "DB_TYPE": "mysql",
        },
    )
    def test_validate_db_config_invalid_port(self, settings: Settings) -> None:
        assert settings.validate_db_config() is False
