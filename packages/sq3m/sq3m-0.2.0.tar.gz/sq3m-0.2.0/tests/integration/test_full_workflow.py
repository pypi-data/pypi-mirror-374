import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import pytest

from sq3m.application.use_cases.database_analyzer import DatabaseAnalyzer
from sq3m.domain.entities.database import Column, DatabaseSchema, DatabaseType, Table
from sq3m.infrastructure.config.env_detector import EnvironmentDetector
from sq3m.infrastructure.history.markdown_history import MarkdownHistory
from sq3m.infrastructure.llm.openai_service import OpenAIService


@pytest.fixture  # type: ignore[misc]
def temp_dirs() -> Generator[Any, None, None]:
    """Create temporary directories for testing."""
    base_temp = tempfile.mkdtemp()
    temp_paths = {
        "base": Path(base_temp),
        "history": Path(base_temp) / "history",
        "faiss": Path(base_temp) / "faiss",
        "config": Path(base_temp) / "config",
    }

    # Create directories
    for path in temp_paths.values():
        path.mkdir(exist_ok=True)

    yield temp_paths

    # Cleanup: Explicitly clean up any chat session files
    try:
        history_dir = temp_paths["history"]
        if history_dir.exists():
            # Remove all .md files (conversation history)
            for md_file in history_dir.glob("*.md"):
                md_file.unlink()
    except Exception:
        pass  # Ignore cleanup errors

    # Final cleanup
    shutil.rmtree(base_temp)


@pytest.fixture  # type: ignore[misc]
def mock_openai_client() -> Any:
    """Mock OpenAI client for testing."""
    client = Mock()

    # Mock chat completion response
    chat_response = Mock()
    chat_response.choices = [Mock()]
    chat_response.choices[
        0
    ].message.content = "This table stores user account information."
    client.chat.completions.create.return_value = chat_response

    # Mock embedding response
    embedding_response = Mock()
    embedding_response.data = [Mock()]
    embedding_response.data[0].embedding = [0.1] * 1536
    client.embeddings.create.return_value = embedding_response

    return client


@pytest.fixture  # type: ignore[misc]
def sample_database_schema() -> Any:
    """Create sample database schema for testing."""
    users_table = Table(
        name="users",
        columns=[
            Column(
                name="id", data_type="INTEGER", is_nullable=False, is_primary_key=True
            ),
            Column(
                name="email",
                data_type="VARCHAR",
                is_nullable=False,
                is_primary_key=False,
            ),
            Column(
                name="password_hash",
                data_type="VARCHAR",
                is_nullable=False,
                is_primary_key=False,
            ),
            Column(
                name="created_at",
                data_type="TIMESTAMP",
                is_nullable=False,
                is_primary_key=False,
            ),
            Column(
                name="updated_at",
                data_type="TIMESTAMP",
                is_nullable=True,
                is_primary_key=False,
            ),
        ],
        indexes=[],
        comment="User accounts and authentication",
    )

    orders_table = Table(
        name="orders",
        columns=[
            Column(
                name="id", data_type="INTEGER", is_nullable=False, is_primary_key=True
            ),
            Column(
                name="user_id",
                data_type="INTEGER",
                is_nullable=False,
                is_primary_key=False,
            ),
            Column(
                name="total_amount",
                data_type="DECIMAL",
                is_nullable=False,
                is_primary_key=False,
            ),
            Column(
                name="status",
                data_type="VARCHAR",
                is_nullable=False,
                is_primary_key=False,
            ),
            Column(
                name="created_at",
                data_type="TIMESTAMP",
                is_nullable=False,
                is_primary_key=False,
            ),
        ],
        indexes=[],
        comment="Customer orders",
    )

    return DatabaseSchema(
        name="ecommerce_db",
        tables=[users_table, orders_table],
        database_type=DatabaseType.MYSQL,
    )


@pytest.fixture  # type: ignore[misc]
def mock_database_repository(sample_database_schema: Any) -> Any:
    """Mock database repository."""
    repo = Mock()
    repo.get_schema.return_value = sample_database_schema
    repo.get_table_sample_rows.side_effect = (
        lambda table_name, limit: [
            {"id": 1, "email": "user1@example.com", "created_at": "2024-01-01"},
            {"id": 2, "email": "user2@example.com", "created_at": "2024-01-02"},
        ]
        if table_name == "users"
        else [
            {"id": 1, "user_id": 1, "total_amount": "99.99", "status": "completed"},
            {"id": 2, "user_id": 2, "total_amount": "149.99", "status": "pending"},
        ]
    )
    return repo


class TestFullWorkflow:
    """Test complete workflow integration."""

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_complete_analysis_workflow(
        self, temp_dirs: Any, mock_openai_client: Any, mock_database_repository: Any
    ) -> None:
        """Test complete database analysis workflow."""

        # 1. Initialize services
        llm_service = OpenAIService(api_key="test-key")
        llm_service.client = mock_openai_client
        llm_service.async_client = AsyncMock()
        llm_service.async_client.chat.completions.create.return_value = (
            mock_openai_client.chat.completions.create.return_value
        )

        analyzer = DatabaseAnalyzer(mock_database_repository, llm_service)

        # 2. Run analysis
        schema = await analyzer.analyze_schema_async()

        # 3. Verify analysis results
        assert len(schema.tables) == 2

        # Verify each table was analyzed
        for table in schema.tables:
            assert table.purpose is not None
            assert table.sample_rows is not None
            assert len(table.sample_rows) == 2

        # Verify purposes were stored
        assert len(analyzer.table_purposes) == 2
        assert "users" in analyzer.table_purposes
        assert "orders" in analyzer.table_purposes

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_rag_integration_workflow(
        self, temp_dirs: Any, mock_openai_client: Any, sample_database_schema: Any
    ) -> None:
        """Test RAG service integration workflow (mocked)."""

        # Mock RAG service functionality
        class MockRAGService:
            def __init__(self) -> None:
                self.metadata: list[dict[str, Any]] = []
                self.index = Mock()

            def add_schema(self, schema: Any) -> None:
                self.metadata = [
                    {"table": table.name, "purpose": table.comment}
                    for table in schema.tables
                ]

            def search_relevant_tables(
                self, query: str, top_k: int = 2
            ) -> list[dict[str, Any]]:
                return [
                    {
                        "table": "users",
                        "relevance_score": 0.9,
                        "purpose": "User accounts",
                    },
                    {
                        "table": "orders",
                        "relevance_score": 0.7,
                        "purpose": "Customer orders",
                    },
                ][:top_k]

        # Initialize mock RAG service
        rag_service = MockRAGService()

        # Add schema to RAG
        rag_service.add_schema(sample_database_schema)

        # Verify tables were added
        assert len(rag_service.metadata) == len(sample_database_schema.tables)

        # Test search functionality
        results = rag_service.search_relevant_tables("find user information", top_k=2)

        assert len(results) == 2
        assert results[0]["relevance_score"] == 0.9
        assert results[1]["relevance_score"] == 0.7

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_history_integration_workflow(
        self, temp_dirs: Any, cleanup_chat_sessions: Any
    ) -> None:
        """Test conversation history integration workflow."""

        history_service = MarkdownHistory(history_dir=str(temp_dirs["history"]))
        cleanup_chat_sessions(history_service)  # Register for cleanup

        # Start session
        await history_service.start_new_session("integration_test", "ecommerce_db")

        # Add user query
        await history_service.add_user_query("Show me all users who placed orders")

        # Add SQL response
        await history_service.add_sql_response(
            sql="SELECT u.* FROM users u JOIN orders o ON u.id = o.user_id",
            explanation="This query joins users and orders tables to find users with orders",
            confidence=0.92,
            execution_result="Found 5 users with orders",
        )

        # Add analysis result
        await history_service.add_analysis_result(
            schema_summary="Analyzed e-commerce database with users and orders tables",
            tables_analyzed=2,
            analysis_time=1.5,
        )

        # Verify session content
        content = await history_service.get_session_content()

        assert "integration_test" in content
        assert "ecommerce_db" in content
        assert "Show me all users who placed orders" in content
        assert "SELECT u.* FROM users u JOIN orders o" in content
        assert "Found 5 users with orders" in content
        assert "**Confidence:** 92.00%" in content
        assert "Analyzed e-commerce database" in content

        # Close session
        session_file = await history_service.close_session()
        assert session_file is not None
        assert session_file.exists()

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_environment_detection_workflow(self, temp_dirs: Any) -> None:
        """Test environment detection and configuration workflow."""

        with patch("pathlib.Path.home", return_value=temp_dirs["config"]):
            detector = EnvironmentDetector()

            # Test environment detection
            env_info = detector.detect_environment()

            assert "system" in env_info
            assert "python_version" in env_info
            assert "config_dir" in env_info

            # Test configuration application
            config = detector.apply_environment_config()

            assert "config_dir" in config
            assert "env_file" in config
            assert "conversations_dir" in config
            assert "faiss_dir" in config

            # Verify directories were created
            config_dir = Path(config["config_dir"])
            assert config_dir.exists()
            assert (config_dir / "conversations").exists()
            assert (config_dir / "faiss_indices").exists()

            # Verify env file was created
            env_file = Path(config["env_file"])
            assert env_file.exists()

            content = env_file.read_text()
            assert "OPENAI_API_KEY" in content
            assert "DB_TYPE" in content

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_end_to_end_workflow(
        self,
        temp_dirs: Any,
        mock_openai_client: Any,
        mock_database_repository: Any,
        sample_database_schema: Any,
        cleanup_chat_sessions: Any,
    ) -> None:
        """Test complete end-to-end workflow."""

        # 1. Environment setup
        with patch("pathlib.Path.home", return_value=temp_dirs["config"]):
            env_detector = EnvironmentDetector()
            config = env_detector.apply_environment_config()

        # 2. Initialize all services
        llm_service = OpenAIService(api_key="test-key")
        llm_service.client = mock_openai_client
        llm_service.async_client = AsyncMock()
        llm_service.async_client.chat.completions.create.return_value = (
            mock_openai_client.chat.completions.create.return_value
        )

        analyzer = DatabaseAnalyzer(mock_database_repository, llm_service)

        # Mock RAG service for end-to-end test
        class MockRAGService:
            def __init__(self) -> None:
                self.metadata: list[dict[str, Any]] = []

            def add_schema(self, schema: Any) -> None:
                self.metadata = [
                    {"table": table.name, "purpose": table.comment}
                    for table in schema.tables
                ]

            def search_relevant_tables(
                self, query: str, top_k: int = 2
            ) -> list[dict[str, Any]]:
                return [
                    {
                        "table": "users",
                        "relevance_score": 0.9,
                        "purpose": "User accounts",
                    },
                    {
                        "table": "orders",
                        "relevance_score": 0.8,
                        "purpose": "Customer orders",
                    },
                ][:top_k]

        rag_service = MockRAGService()

        history_service = MarkdownHistory(history_dir=str(temp_dirs["history"]))
        cleanup_chat_sessions(history_service)  # Register for cleanup

        # 3. Run complete workflow

        # Start conversation session
        await history_service.start_new_session("e2e_test", "ecommerce_db")

        # Analyze database schema
        schema = await analyzer.analyze_schema_async()

        await history_service.add_analysis_result(
            schema_summary=f"Analyzed {schema.name} with {len(schema.tables)} tables",
            tables_analyzed=len(schema.tables),
            analysis_time=2.0,
        )

        # Add schema to RAG
        rag_service.add_schema(schema)

        # Simulate user query
        user_query = "Find all users who have placed orders in the last month"
        await history_service.add_user_query(user_query)

        # Search for relevant tables using RAG

        relevant_tables = rag_service.search_relevant_tables(user_query, top_k=2)
        assert len(relevant_tables) >= 1

        # Generate SQL (mocked)
        sql_query = "SELECT u.* FROM users u JOIN orders o ON u.id = o.user_id WHERE o.created_at >= DATE_SUB(NOW(), INTERVAL 1 MONTH)"

        await history_service.add_sql_response(
            sql=sql_query,
            explanation="Query joins users and orders, filtering for recent orders",
            confidence=0.88,
        )

        # Close session
        session_file = await history_service.close_session()

        # 4. Verify complete workflow
        assert session_file is not None

        # Verify session content includes all steps
        content = session_file.read_text()
        assert "e2e_test" in content
        assert "ecommerce_db" in content
        assert user_query in content
        assert sql_query in content
        assert "Schema Analysis" in content
        assert "Generated SQL" in content

        # Verify RAG service has data
        assert len(rag_service.metadata) == len(schema.tables)

        # Verify analyzer has purposes
        assert len(analyzer.table_purposes) == len(schema.tables)

        # Verify configuration was applied
        assert Path(config["config_dir"]).exists()
        assert Path(config["env_file"]).exists()
