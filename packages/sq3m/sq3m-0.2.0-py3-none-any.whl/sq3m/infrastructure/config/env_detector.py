from __future__ import annotations

import os
import platform
from pathlib import Path


class EnvironmentDetector:
    """Detects the user's environment and applies appropriate configuration."""

    def __init__(self) -> None:
        self.system = platform.system().lower()
        self.home_dir = Path.home()
        self.config_dir = self._get_config_dir()

    def _get_config_dir(self) -> Path:
        """Get the appropriate configuration directory based on the OS.

        Notes:
            - For Linux/Unix, prefer XDG_CONFIG_HOME only if it points inside the
              current user's home directory. This avoids CI environments leaking
              global XDG settings into tests that patch Path.home().
        """
        if self.system == "windows":
            config_dir = (
                Path(os.getenv("APPDATA", self.home_dir / "AppData" / "Roaming"))
                / "sq3m"
            )
        elif self.system == "darwin":  # macOS
            config_dir = self.home_dir / "Library" / "Application Support" / "sq3m"
        else:  # Linux and other Unix-like systems
            home_config = self.home_dir / ".config"
            xdg_env = os.getenv("XDG_CONFIG_HOME")
            if xdg_env:
                xdg_path = Path(xdg_env)
                # Use XDG only if it points under the current (possibly patched) home
                if str(xdg_path).startswith(str(self.home_dir)):
                    config_dir = xdg_path / "sq3m"
                else:
                    config_dir = home_config / "sq3m"
            else:
                config_dir = home_config / "sq3m"

        # Create config directory if it doesn't exist
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir

    def detect_environment(self) -> dict[str, str]:
        """Detect environment details and return configuration."""
        env_info = {
            "system": self.system,
            "architecture": platform.architecture()[0],
            "python_version": platform.python_version(),
            "home_dir": str(self.home_dir),
            "config_dir": str(self.config_dir),
        }

        # Add OS-specific paths
        if self.system == "windows":
            env_info.update(
                {
                    "shell": "cmd" if os.getenv("COMSPEC") else "powershell",
                    "path_separator": "\\",
                    "line_ending": "\r\n",
                    "default_db_port_mysql": "3306",
                    "default_db_port_postgresql": "5432",
                }
            )
        else:  # Unix-like systems (macOS, Linux)
            shell = os.getenv("SHELL", "/bin/bash")
            env_info.update(
                {
                    "shell": Path(shell).name,
                    "path_separator": "/",
                    "line_ending": "\n",
                    "default_db_port_mysql": "3306",
                    "default_db_port_postgresql": "5432",
                }
            )

        return env_info

    def get_env_file_path(self) -> Path:
        """Get the path where environment variables should be stored."""
        return self.config_dir / ".env"

    def create_default_env_file(self) -> Path:
        """Create a default .env file with template values."""
        env_file = self.get_env_file_path()

        if not env_file.exists():
            default_content = f"""# sq3m Configuration
# Generated automatically for {self.system}

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_BASE_URL=

# Database Configuration Templates
# Uncomment and configure as needed

# MySQL
# DB_TYPE=mysql
# DB_HOST=localhost
# DB_PORT=3306
# DB_NAME=your_database
# DB_USERNAME=your_username
# DB_PASSWORD=your_password

# PostgreSQL
# DB_TYPE=postgresql
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=your_database
# DB_USERNAME=your_username
# DB_PASSWORD=your_password


# Application Settings
HISTORY_DIR={self.config_dir / "conversations"}
FAISS_INDEX_DIR={self.config_dir / "faiss_indices"}
LOG_LEVEL=INFO

# System Prompt Configuration
# Option 1: Use absolute path to prompt file (supports .txt, .md)
# SYSTEM_PROMPT_PATH=/path/to/your/custom_prompt.md

# Option 2: Use filename in config directory (supports .txt, .md)
# SYSTEM_PROMPT_FILE=my_system_prompt.md
"""

            env_file.write_text(default_content, encoding="utf-8")

        return env_file

    def get_default_db_config(self, db_type: str = "mysql") -> dict[str, str]:
        """Get default database configuration for the current environment."""
        defaults = {
            "mysql": {
                "host": "localhost",
                "port": "3306",
                "charset": "utf8mb4",
            },
            "postgresql": {
                "host": "localhost",
                "port": "5432",
                "sslmode": "prefer",
            },
        }

        return defaults.get(db_type.lower(), {})

    def detect_db_clients(self) -> dict[str, bool]:
        """Detect available database clients on the system."""
        clients = {}

        # Common database client executables to check for
        client_commands = {
            "mysql": ["mysql", "mysqladmin"],
            "postgresql": ["psql", "pg_dump"],
        }

        for db_type, commands in client_commands.items():
            clients[db_type] = any(self._command_exists(cmd) for cmd in commands)

        return clients

    # Backwards-compat alias used in tests or external code
    def detect_database_clients(self) -> dict[str, bool]:
        return self.detect_db_clients()

    def _command_exists(self, command: str) -> bool:
        """Check if a command exists in the system PATH."""
        if self.system == "windows":
            # On Windows, check both with and without .exe extension
            from shutil import which

            return which(command) is not None or which(f"{command}.exe") is not None
        else:
            # On Unix-like systems
            from shutil import which

            return which(command) is not None

    def get_recommended_settings(self) -> dict[str, str]:
        """Get recommended settings based on the detected environment."""
        settings = {}

        # Get detected clients (use alias so tests can patch it)
        db_clients = self.detect_database_clients()

        # Recommend database types based on available clients
        available_dbs = [db for db, available in db_clients.items() if available]
        if available_dbs:
            settings["recommended_db_types"] = ",".join(available_dbs)

        # Performance settings based on system specs
        import psutil

        memory_gb = psutil.virtual_memory().total / (1024**3)
        cpu_count = psutil.cpu_count() or 1  # Default to 1 if None

        if memory_gb >= 8 and cpu_count >= 4:
            settings["performance_level"] = "high"
            settings["faiss_dimension"] = "1536"
            settings["max_concurrent_requests"] = "5"
        elif memory_gb >= 4 and cpu_count >= 2:
            settings["performance_level"] = "medium"
            settings["faiss_dimension"] = "1536"
            settings["max_concurrent_requests"] = "3"
        else:
            settings["performance_level"] = "low"
            settings["faiss_dimension"] = "768"
            settings["max_concurrent_requests"] = "1"

        return settings

    def apply_environment_config(self) -> dict[str, str]:
        """Apply environment-specific configuration and return the config."""
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Create default env file if it doesn't exist
        env_file = self.create_default_env_file()

        # Create conversations directory
        conversations_dir = self.config_dir / "conversations"
        conversations_dir.mkdir(exist_ok=True)

        # Create FAISS indices directory
        faiss_dir = self.config_dir / "faiss_indices"
        faiss_dir.mkdir(exist_ok=True)

        # Create default system prompt file in config directory if it doesn't exist
        self._create_default_system_prompt_if_needed()

        # Return configuration info
        return {
            "config_dir": str(self.config_dir),
            "env_file": str(env_file),
            "conversations_dir": str(conversations_dir),
            "faiss_dir": str(faiss_dir),
            "system": self.system,
        }

    def _create_default_system_prompt_if_needed(self) -> None:
        """Create a default system prompt file in config directory if none exists."""
        prompt_file = self.config_dir / "system_prompt.md"

        if not prompt_file.exists():
            # Import here to avoid circular imports
            try:
                from sq3m.infrastructure.prompts.prompt_loader import PromptLoader

                loader = PromptLoader()
                default_content = loader.load_system_prompt()
                prompt_file.write_text(default_content, encoding="utf-8")
            except Exception:
                # Fallback content if PromptLoader is not available
                fallback_content = """You are a database expert and SQL specialist.
Generate accurate SQL queries and analyze database schemas effectively."""
                prompt_file.write_text(fallback_content, encoding="utf-8")
