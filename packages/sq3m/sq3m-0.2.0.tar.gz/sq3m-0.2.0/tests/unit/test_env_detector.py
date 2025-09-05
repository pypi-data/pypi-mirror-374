import os
import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

import pytest

from sq3m.infrastructure.config.env_detector import EnvironmentDetector


@pytest.fixture  # type: ignore[misc]
def temp_home_dir() -> Generator[Any, None, None]:
    """Create a temporary home directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


class TestEnvironmentDetector:
    @patch("platform.system")
    @patch("pathlib.Path.home")
    def test_init_windows(
        self, mock_home: Any, mock_system: Any, temp_home_dir: Any
    ) -> None:
        """Test initialization on Windows."""
        mock_system.return_value = "Windows"
        mock_home.return_value = temp_home_dir

        with patch.dict(
            os.environ,
            {"APPDATA": str(temp_home_dir / "AppData" / "Roaming")},
            clear=False,
        ):
            detector = EnvironmentDetector()

            assert detector.system == "windows"
            assert detector.home_dir == temp_home_dir
            expected_config = temp_home_dir / "AppData" / "Roaming" / "sq3m"
            assert detector.config_dir == expected_config
            assert detector.config_dir.exists()

    @patch("platform.system")
    @patch("pathlib.Path.home")
    def test_init_macos(
        self, mock_home: Any, mock_system: Any, temp_home_dir: Any
    ) -> None:
        """Test initialization on macOS."""
        mock_system.return_value = "Darwin"
        mock_home.return_value = temp_home_dir

        detector = EnvironmentDetector()

        assert detector.system == "darwin"
        assert detector.home_dir == temp_home_dir
        expected_config = temp_home_dir / "Library" / "Application Support" / "sq3m"
        assert detector.config_dir == expected_config
        assert detector.config_dir.exists()

    @patch("platform.system")
    @patch("pathlib.Path.home")
    def test_init_linux(
        self, mock_home: Any, mock_system: Any, temp_home_dir: Any
    ) -> None:
        """Test initialization on Linux."""
        mock_system.return_value = "Linux"
        mock_home.return_value = temp_home_dir

        detector = EnvironmentDetector()

        assert detector.system == "linux"
        assert detector.home_dir == temp_home_dir
        expected_config = temp_home_dir / ".config" / "sq3m"
        assert detector.config_dir == expected_config
        assert detector.config_dir.exists()

    @patch("platform.system")
    @patch("pathlib.Path.home")
    def test_init_linux_with_xdg_config(
        self, mock_home: Any, mock_system: Any, temp_home_dir: Any
    ) -> None:
        """Test initialization on Linux with XDG_CONFIG_HOME set."""
        mock_system.return_value = "Linux"
        mock_home.return_value = temp_home_dir

        xdg_config = temp_home_dir / "custom_config"
        with patch.dict(os.environ, {"XDG_CONFIG_HOME": str(xdg_config)}, clear=False):
            detector = EnvironmentDetector()

            expected_config = xdg_config / "sq3m"
            assert detector.config_dir == expected_config
            assert detector.config_dir.exists()

    @patch("platform.system")
    @patch("platform.architecture")
    @patch("platform.python_version")
    @patch("pathlib.Path.home")
    def test_detect_environment_windows(
        self,
        mock_home: Any,
        mock_python_ver: Any,
        mock_arch: Any,
        mock_system: Any,
        temp_home_dir: Any,
    ) -> None:
        """Test environment detection on Windows."""
        mock_system.return_value = "Windows"
        mock_arch.return_value = ("64bit", "WindowsPE")
        mock_python_ver.return_value = "3.10.0"
        mock_home.return_value = temp_home_dir

        detector = EnvironmentDetector()
        env_info = detector.detect_environment()

        assert env_info["system"] == "windows"
        assert env_info["architecture"] == "64bit"
        assert env_info["python_version"] == "3.10.0"
        assert env_info["path_separator"] == "\\"
        assert env_info["line_ending"] == "\r\n"
        assert env_info["default_db_port_mysql"] == "3306"

    @patch("platform.system")
    @patch("platform.architecture")
    @patch("platform.python_version")
    @patch("pathlib.Path.home")
    def test_detect_environment_unix(
        self,
        mock_home: Any,
        mock_python_ver: Any,
        mock_arch: Any,
        mock_system: Any,
        temp_home_dir: Any,
    ) -> None:
        """Test environment detection on Unix-like systems."""
        mock_system.return_value = "Linux"
        mock_arch.return_value = ("64bit", "ELF")
        mock_python_ver.return_value = "3.11.0"
        mock_home.return_value = temp_home_dir

        with patch.dict(os.environ, {"SHELL": "/bin/zsh"}, clear=False):
            detector = EnvironmentDetector()
            env_info = detector.detect_environment()

            assert env_info["system"] == "linux"
            assert env_info["shell"] == "zsh"
            assert env_info["path_separator"] == "/"
            assert env_info["line_ending"] == "\n"

    @patch("platform.system")
    @patch("pathlib.Path.home")
    def test_create_default_env_file(
        self, mock_home: Any, mock_system: Any, temp_home_dir: Any
    ) -> None:
        """Test creating default environment file."""
        mock_system.return_value = "Linux"
        mock_home.return_value = temp_home_dir

        detector = EnvironmentDetector()
        env_file = detector.create_default_env_file()

        assert env_file.exists()
        assert env_file == detector.get_env_file_path()

        content = env_file.read_text()
        assert "OPENAI_API_KEY=your_openai_api_key_here" in content
        assert "DB_TYPE=mysql" in content
        assert "HISTORY_DIR=" in content
        assert "FAISS_INDEX_DIR=" in content

    @patch("platform.system")
    @patch("pathlib.Path.home")
    def test_create_default_env_file_exists(
        self, mock_home: Any, mock_system: Any, temp_home_dir: Any
    ) -> None:
        """Test that existing env file is not overwritten."""
        mock_system.return_value = "Linux"
        mock_home.return_value = temp_home_dir

        detector = EnvironmentDetector()
        env_file = detector.get_env_file_path()

        # Create existing file
        env_file.parent.mkdir(parents=True, exist_ok=True)
        original_content = "EXISTING_CONFIG=value"
        env_file.write_text(original_content)

        # Try to create default
        result_file = detector.create_default_env_file()

        assert result_file == env_file
        assert env_file.read_text() == original_content  # Should not be overwritten

    def test_get_database_defaults(self, temp_home_dir: Any) -> None:
        """Test getting database defaults."""
        with patch("pathlib.Path.home", return_value=temp_home_dir):
            detector = EnvironmentDetector()

            mysql_defaults = detector.get_default_db_config("mysql")
            assert mysql_defaults["host"] == "localhost"
            assert mysql_defaults["port"] == "3306"
            assert mysql_defaults["charset"] == "utf8mb4"

            pg_defaults = detector.get_default_db_config("postgresql")
            assert pg_defaults["host"] == "localhost"
            assert pg_defaults["port"] == "5432"

            # Test unknown database type
            unknown_defaults = detector.get_default_db_config("unknown")
            assert unknown_defaults == {}

    @patch("shutil.which")
    def test_detect_database_clients(self, mock_which: Any, temp_home_dir: Any) -> None:
        """Test detecting available database clients."""
        with patch("pathlib.Path.home", return_value=temp_home_dir):
            detector = EnvironmentDetector()

            # Mock which() to return paths for some clients
            def mock_which_side_effect(cmd: str) -> str | None:
                if cmd in ["mysql", "psql"]:
                    return "/usr/bin/" + cmd
                return None

            mock_which.side_effect = mock_which_side_effect

            clients = detector.detect_db_clients()

            assert clients["mysql"] is True
            assert clients["postgresql"] is True

    @patch("shutil.which")
    def test_command_exists_windows(self, mock_which: Any, temp_home_dir: Any) -> None:
        """Test command existence check on Windows."""
        with (
            patch("pathlib.Path.home", return_value=temp_home_dir),
            patch("platform.system", return_value="Windows"),
        ):
            detector = EnvironmentDetector()

            # Mock which() to simulate Windows behavior
            def mock_which_side_effect(cmd: str) -> str | None:
                if cmd == "mysql.exe":
                    return "C:\\Program Files\\MySQL\\bin\\mysql.exe"
                return None

            mock_which.side_effect = mock_which_side_effect

            # Should check both mysql and mysql.exe
            detector._command_exists("mysql")

            assert mock_which.call_count >= 1

    @patch("psutil.virtual_memory")
    @patch("psutil.cpu_count")
    def test_get_recommended_settings_high_performance(
        self, mock_cpu_count: Any, mock_virtual_memory: Any, temp_home_dir: Any
    ) -> None:
        """Test recommended settings for high-performance system."""
        with patch("pathlib.Path.home", return_value=temp_home_dir):
            # Mock high-performance system
            mock_memory = Mock()
            mock_memory.total = 16 * 1024**3  # 16GB
            mock_virtual_memory.return_value = mock_memory
            mock_cpu_count.return_value = 8

            detector = EnvironmentDetector()
            with patch.object(
                detector,
                "detect_database_clients",
                return_value={"mysql": True, "postgresql": False},
            ):
                settings = detector.get_recommended_settings()

                assert settings["performance_level"] == "high"
            assert settings["faiss_dimension"] == "1536"
            assert settings["max_concurrent_requests"] == "5"
            assert settings["recommended_db_types"] == "mysql"

    @patch("psutil.virtual_memory")
    @patch("psutil.cpu_count")
    def test_get_recommended_settings_low_performance(
        self, mock_cpu_count: Any, mock_virtual_memory: Any, temp_home_dir: Any
    ) -> None:
        """Test recommended settings for low-performance system."""
        with patch("pathlib.Path.home", return_value=temp_home_dir):
            # Mock low-performance system
            mock_memory = Mock()
            mock_memory.total = 2 * 1024**3  # 2GB
            mock_virtual_memory.return_value = mock_memory
            mock_cpu_count.return_value = 2

            detector = EnvironmentDetector()
            with patch.object(detector, "detect_database_clients", return_value={}):
                settings = detector.get_recommended_settings()

                assert settings["performance_level"] == "low"
            assert settings["faiss_dimension"] == "768"
            assert settings["max_concurrent_requests"] == "1"

    @patch("platform.system")
    @patch("pathlib.Path.home")
    def test_apply_environment_config(
        self, mock_home: Any, mock_system: Any, temp_home_dir: Any
    ) -> None:
        """Test applying environment configuration."""
        mock_system.return_value = "Linux"
        mock_home.return_value = temp_home_dir

        detector = EnvironmentDetector()
        config = detector.apply_environment_config()

        # Verify returned configuration
        assert "config_dir" in config
        assert "env_file" in config
        assert "conversations_dir" in config
        assert "faiss_dir" in config
        assert config["system"] == "linux"

        # Verify directories were created
        config_dir = Path(config["config_dir"])
        assert config_dir.exists()
        assert (config_dir / "conversations").exists()
        assert (config_dir / "faiss_indices").exists()

        # Verify env file was created
        env_file = Path(config["env_file"])
        assert env_file.exists()
