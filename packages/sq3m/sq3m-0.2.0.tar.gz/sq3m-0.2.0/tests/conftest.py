from __future__ import annotations

import asyncio
import shutil
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

if TYPE_CHECKING:
    from collections.abc import Callable, Generator

# Import all fixtures from the fixtures module
pytest_plugins = ["tests.fixtures.database_fixtures"]


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )


@pytest.fixture(autouse=True)  # type: ignore[misc]
def _clear_env_for_determinism(monkeypatch: Any) -> None:
    """Ensure environment-dependent settings don't leak into tests.

    Some environments may define variables like OPENAI_MODEL via a local .env or
    shell session. Clear a few known keys so tests remain deterministic.
    """
    for key in [
        "OPENAI_MODEL",
    ]:
        monkeypatch.delenv(key, raising=False)


@pytest.fixture(scope="function")  # type: ignore[misc]
def cleanup_chat_sessions() -> Generator[Callable[[Any], None], None, None]:
    """Fixture to ensure chat sessions are cleaned up after each test."""
    chat_services = []
    session_files = []

    def register_service(service: Any) -> None:
        """Register a chat service for cleanup."""
        chat_services.append(service)
        # Also track the service's history directory for cleanup
        if hasattr(service, "history_dir"):
            session_files.extend(service.history_dir.glob("*.md"))

    yield register_service

    # Cleanup after test
    for service in chat_services:
        try:
            # Close active sessions
            if (
                hasattr(service, "close_session")
                and hasattr(service, "current_session_file")
                and service.current_session_file is not None
            ):
                asyncio.run(service.close_session())

            # Remove all session files from the service's history directory
            if hasattr(service, "history_dir") and service.history_dir.exists():
                for md_file in service.history_dir.glob("*.md"):
                    try:
                        if md_file.is_file() and _is_session_file(md_file):
                            md_file.unlink()
                    except Exception:
                        pass

        except Exception:
            pass  # Ignore cleanup errors

    # Additional cleanup for any tracked session files
    for session_file in session_files:
        try:
            if session_file.exists() and session_file.is_file():
                session_file.unlink()
        except Exception:
            pass


@pytest.fixture(scope="function")  # type: ignore[misc]
def temp_chat_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for chat sessions."""
    temp_dir = tempfile.mkdtemp(prefix="sq3m_test_chat_")
    temp_path = Path(temp_dir)

    yield temp_path

    # Cleanup: Remove all chat session files
    try:
        if temp_path.exists():
            # Remove all .md files (conversation history)
            for md_file in temp_path.glob("*.md"):
                md_file.unlink(missing_ok=True)
            # Remove directory
            shutil.rmtree(temp_dir, ignore_errors=True)
    except Exception:
        pass  # Ignore cleanup errors


@pytest.fixture(autouse=True)  # type: ignore[misc]
def cleanup_temp_files() -> Generator[None, None, None]:
    """Auto-cleanup fixture to remove temporary files after each test."""
    # Track directories and files created during test
    original_cwd = Path.cwd()

    yield

    # Clean up any remaining temporary chat files in multiple locations
    import tempfile
    import time

    current_time = time.time()

    # List of directories to check for cleanup
    cleanup_dirs = [
        Path(tempfile.gettempdir()),  # System temp directory
        original_cwd,  # Current working directory
        original_cwd / "tests",  # Tests directory
        Path(),  # Current directory when test runs
    ]

    for temp_dir in cleanup_dirs:
        if not temp_dir.exists():
            continue

        try:
            # Patterns for session/conversation markdown files
            patterns = [
                "*.md",  # All markdown files
                "*session*.md",
                "*conversation*.md",
                "*chat*.md",
                "sq3m_test_*",
                "*_test_session_*",
                "*sq3m*session*.md",
                "[0-9]*_[0-9]*_*.md",  # Timestamp pattern files
            ]

            for pattern in patterns:
                for file in temp_dir.glob(pattern):
                    if file.is_file():
                        try:
                            # Check if file looks like a session file by checking content
                            if _is_session_file(file) and _is_recent_test_file(
                                file, current_time
                            ):
                                file.unlink()
                        except Exception:
                            pass  # Ignore individual file cleanup errors
        except Exception:
            pass  # Ignore directory-level cleanup errors


def _is_session_file(file_path: Path) -> bool:
    """Check if file is likely a conversation session file."""
    try:
        # Check filename patterns
        name = file_path.name.lower()
        if any(
            keyword in name for keyword in ["session", "conversation", "chat", "sq3m"]
        ):
            return True

        # Check if filename matches timestamp pattern (YYYYMMDD_HHMMSS_*.md)
        if name.endswith(".md"):
            parts = name.replace(".md", "").split("_")
            if len(parts) >= 3 and parts[0].isdigit() and parts[1].isdigit():
                return True

        # Check file content for session markers
        content = file_path.read_text(encoding="utf-8", errors="ignore")[
            :500
        ]  # First 500 chars
        session_markers = [
            "# sq3m Conversation Session",
            "**Session ID:**",
            "**Started:**",
            "## User Query",
            "## Generated SQL",
            "sq3m Conversation",
        ]

        return any(marker in content for marker in session_markers)
    except Exception:
        return False


def _is_recent_test_file(file_path: Path, current_time: float) -> bool:
    """Check if file was created recently and is likely from tests."""
    try:
        # Only remove files created within the last 2 hours to be safe
        file_age = current_time - file_path.stat().st_ctime
        return file_age < 7200  # 2 hours in seconds
    except Exception:
        return False
