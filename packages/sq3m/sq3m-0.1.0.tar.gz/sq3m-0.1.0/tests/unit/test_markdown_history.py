import shutil
import tempfile
from collections.abc import Generator
from datetime import datetime
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from sq3m.infrastructure.history.markdown_history import MarkdownHistory


@pytest.fixture  # type: ignore[misc]
def temp_history_dir() -> Generator[str, None, None]:
    """Create a temporary directory for conversation history."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture  # type: ignore[misc]
def history_service(temp_history_dir: str, cleanup_chat_sessions: Any) -> Any:
    """Create MarkdownHistory instance with temporary directory."""
    service = MarkdownHistory(history_dir=temp_history_dir)
    # Register for automatic cleanup
    cleanup_chat_sessions(service)
    return service


class TestMarkdownHistory:
    def test_init(self, temp_history_dir: str) -> None:
        """Test MarkdownHistory initialization."""
        service = MarkdownHistory(history_dir=temp_history_dir)

        assert service.history_dir == Path(temp_history_dir)
        assert service.history_dir.exists()
        assert service.current_session_file is None
        assert service.session_id is None

    def test_get_session_filename(self, history_service: Any) -> None:
        """Test session filename generation."""
        with patch(
            "sq3m.infrastructure.history.markdown_history.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 10, 30, 45)

            filename = history_service._get_session_filename("test_session_123")

            assert filename == "20240101_103045_test_session_123.md"

    def test_get_session_filename_special_chars(self, history_service: Any) -> None:
        """Test session filename generation with special characters."""
        with patch(
            "sq3m.infrastructure.history.markdown_history.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 10, 30, 45)

            filename = history_service._get_session_filename(
                "test/session:with*special"
            )

            # Special characters should be removed
            assert filename == "20240101_103045_testsessionwithspecial.md"

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_start_new_session(self, history_service: Any) -> None:
        """Test starting a new conversation session."""
        await history_service.start_new_session("test_session", "test_db")

        assert history_service.session_id == "test_session"
        assert history_service.current_session_file is not None
        assert history_service.current_session_file.exists()

        # Check file content
        content = history_service.current_session_file.read_text()
        assert "# sq3m Conversation Session" in content
        assert "**Session ID:** test_session" in content
        assert "**Database:** test_db" in content

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_add_user_query(self, history_service: Any) -> None:
        """Test adding user query to history."""
        await history_service.start_new_session("test", "db")

        await history_service.add_user_query("SELECT * FROM users")

        content = await history_service.get_session_content()
        assert "## User Query" in content
        assert "SELECT * FROM users" in content

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_add_user_query_auto_start_session(
        self, history_service: Any
    ) -> None:
        """Test adding user query auto-starts session if none exists."""
        await history_service.add_user_query("SELECT * FROM users")

        assert history_service.session_id == "default"
        assert history_service.current_session_file is not None

        content = await history_service.get_session_content()
        assert "SELECT * FROM users" in content

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_add_sql_response(self, history_service: Any) -> None:
        """Test adding SQL response to history."""
        await history_service.start_new_session("test", "db")

        await history_service.add_sql_response(
            sql="SELECT id, email FROM users",
            explanation="This query retrieves user IDs and emails",
            confidence=0.95,
            execution_result="2 rows returned",
        )

        content = await history_service.get_session_content()
        assert "## Generated SQL" in content
        assert "**Confidence:** 95.00%" in content
        assert "```sql" in content
        assert "SELECT id, email FROM users" in content
        assert "This query retrieves user IDs and emails" in content
        assert "**Execution Result:**" in content
        assert "2 rows returned" in content

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_add_sql_response_no_execution_result(
        self, history_service: Any
    ) -> None:
        """Test adding SQL response without execution result."""
        await history_service.start_new_session("test", "db")

        await history_service.add_sql_response(
            sql="SELECT * FROM users", explanation="Get all users", confidence=0.8
        )

        content = await history_service.get_session_content()
        assert "## Generated SQL" in content
        assert "**Execution Result:**" not in content

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_add_analysis_result(self, history_service: Any) -> None:
        """Test adding schema analysis results."""
        await history_service.start_new_session("test", "db")

        schema_summary = "Analyzed database with 5 tables: users, orders, products, categories, reviews"

        await history_service.add_analysis_result(
            schema_summary=schema_summary, tables_analyzed=5, analysis_time=2.5
        )

        content = await history_service.get_session_content()
        assert "## Schema Analysis" in content
        assert "**Tables Analyzed:** 5" in content
        assert "**Analysis Time:** 2.50s" in content
        assert schema_summary in content

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_add_error(self, history_service: Any) -> None:
        """Test adding error information."""
        await history_service.start_new_session("test", "db")

        await history_service.add_error("Connection timeout", "Database Error")

        content = await history_service.get_session_content()
        assert "## Database Error" in content
        assert "Connection timeout" in content

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_add_custom_entry(self, history_service: Any) -> None:
        """Test adding custom entry."""
        await history_service.start_new_session("test", "db")

        await history_service.add_custom_entry("Custom Info", "This is custom content")

        content = await history_service.get_session_content()
        assert "## Custom Info" in content
        assert "This is custom content" in content

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_close_session(self, history_service: Any) -> None:
        """Test closing a session."""
        await history_service.start_new_session("test", "db")
        session_file = history_service.current_session_file

        closed_file = await history_service.close_session()

        assert closed_file == session_file
        assert history_service.current_session_file is None
        assert history_service.session_id is None

        # Check session end marker was added
        content = session_file.read_text()
        assert "**Session Ended:**" in content

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_close_session_no_active_session(self, history_service: Any) -> None:
        """Test closing session when no active session."""
        result = await history_service.close_session()
        assert result is None

    def test_list_sessions(self, history_service: Any) -> None:
        """Test listing conversation sessions."""
        # Create some test session files
        session1 = history_service.history_dir / "20240101_100000_session1.md"
        session2 = history_service.history_dir / "20240101_110000_session2.md"
        session3 = history_service.history_dir / "20240101_120000_session3.md"

        session1.write_text("Session 1")
        session2.write_text("Session 2")
        session3.write_text("Session 3")

        # Update modification times to ensure consistent ordering
        import os
        import time

        now = time.time()
        os.utime(session1, (now - 300, now - 300))  # 5 minutes ago
        os.utime(session2, (now - 200, now - 200))  # 3+ minutes ago
        os.utime(session3, (now - 100, now - 100))  # 1+ minutes ago

        sessions = history_service.list_sessions()

        assert len(sessions) == 3
        # Should be sorted by modification time, most recent first
        assert sessions[0].name.endswith("session3.md")
        assert sessions[1].name.endswith("session2.md")
        assert sessions[2].name.endswith("session1.md")

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_get_recent_sessions(self, history_service: Any) -> None:
        """Test getting recent session information."""
        # Create a test session file with content
        session_file = history_service.history_dir / "test_session.md"
        content = """# sq3m Conversation Session

**Session ID:** test_123
**Started:** 2024-01-01 10:00:00
**Database:** test_db

---

Some content here
"""
        session_file.write_text(content)

        sessions = await history_service.get_recent_sessions(limit=5)

        assert len(sessions) == 1
        session_info = sessions[0]
        assert session_info["filename"] == "test_session.md"
        assert session_info["session_id"] == "test_123"
        assert session_info["database"] == "test_db"
        assert "created" in session_info
        assert "modified" in session_info
        assert "size" in session_info

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_get_recent_sessions_with_error(self, history_service: Any) -> None:
        """Test getting recent sessions when file read error occurs."""
        # Create a problematic file
        session_file = history_service.history_dir / "corrupted.md"
        session_file.write_text("corrupted content")

        # Mock aiofiles.open to raise an exception
        with patch(
            "sq3m.infrastructure.history.markdown_history.aiofiles.open",
            side_effect=OSError("Mock error"),
        ):
            sessions = await history_service.get_recent_sessions()

            assert len(sessions) == 1
            session_info = sessions[0]
            assert "error" in session_info
            assert session_info["error"] == "Mock error"

    def test_get_current_session_info_active(self, history_service: Any) -> None:
        """Test getting current session info when session is active."""
        # Manually set up an active session
        history_service.session_id = "test_session"
        history_service.current_session_file = history_service.history_dir / "test.md"
        history_service.current_session_file.write_text("test content")

        info = history_service.get_current_session_info()

        assert info["active"] is True
        assert info["session_id"] == "test_session"
        assert info["filename"] == "test.md"
        assert "created" in info

    def test_get_current_session_info_inactive(self, history_service: Any) -> None:
        """Test getting current session info when no active session."""
        info = history_service.get_current_session_info()

        assert info["active"] is False
        assert "session_id" not in info
