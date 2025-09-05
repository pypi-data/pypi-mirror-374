"""Tests for embedding service."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from sq3m.domain.entities.table_summary import TableSummary
from sq3m.infrastructure.llm.embedding_service import (
    EmbeddingService,
    EmbeddingServiceError,
)


class TestEmbeddingService:
    """Test cases for EmbeddingService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.api_key = "test-api-key"
        self.service = EmbeddingService(self.api_key)

    @patch("sq3m.infrastructure.llm.embedding_service.OpenAI")
    def test_initialization(self, mock_openai):
        """Test EmbeddingService initialization."""
        service = EmbeddingService("test-key", "test-model")

        mock_openai.assert_called_once_with(api_key="test-key")
        assert service.model == "test-model"

    @patch("sq3m.infrastructure.llm.embedding_service.OpenAI")
    def test_generate_embedding_success(self, mock_openai):
        """Test successful embedding generation."""
        # Mock the OpenAI client response
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3])]
        mock_client.embeddings.create.return_value = mock_response

        service = EmbeddingService("test-key")
        result = service.generate_embedding("test text")

        assert result == [0.1, 0.2, 0.3]
        mock_client.embeddings.create.assert_called_once_with(
            input="test text", model="text-embedding-3-small"
        )

    @patch("sq3m.infrastructure.llm.embedding_service.OpenAI")
    def test_generate_embedding_failure(self, mock_openai):
        """Test embedding generation failure."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_client.embeddings.create.side_effect = Exception("API Error")

        service = EmbeddingService("test-key")

        with pytest.raises(
            EmbeddingServiceError,
            match="Unexpected error during embedding generation: API Error",
        ):
            service.generate_embedding("test text")

    @patch("sq3m.infrastructure.llm.embedding_service.OpenAI")
    def test_generate_embeddings_batch_success(self, mock_openai):
        """Test successful batch embedding generation."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_response.data = [
            Mock(embedding=[0.1, 0.2, 0.3]),
            Mock(embedding=[0.4, 0.5, 0.6]),
        ]
        mock_client.embeddings.create.return_value = mock_response

        service = EmbeddingService("test-key")
        texts = ["text1", "text2"]
        result = service.generate_embeddings_batch(texts)

        expected = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        assert result == expected

        mock_client.embeddings.create.assert_called_once_with(
            input=texts, model="text-embedding-3-small"
        )

    @patch("sq3m.infrastructure.llm.embedding_service.OpenAI")
    def test_generate_embeddings_batch_failure(self, mock_openai):
        """Test batch embedding generation failure."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_client.embeddings.create.side_effect = Exception("Batch API Error")

        service = EmbeddingService("test-key")

        with pytest.raises(
            EmbeddingServiceError,
            match="Unexpected error during batch embedding generation: Batch API Error",
        ):
            service.generate_embeddings_batch(["text1", "text2"])

    def test_create_table_summary_text_complete(self):
        """Test creating table summary text with all components."""
        service = EmbeddingService("test-key")

        result = service.create_table_summary_text(
            "users",
            "Store user information",
            "id (int), name (varchar), email (varchar)",
        )

        expected = "Table: users | Purpose: Store user information | Schema: id (int), name (varchar), email (varchar)"
        assert result == expected

    def test_create_table_summary_text_minimal(self):
        """Test creating table summary text with minimal components."""
        service = EmbeddingService("test-key")

        result = service.create_table_summary_text(
            "logs", None, "timestamp (datetime), message (text)"
        )

        expected = "Table: logs | Schema: timestamp (datetime), message (text)"
        assert result == expected

    def test_create_table_summary_text_empty_purpose(self):
        """Test creating table summary text with empty purpose."""
        service = EmbeddingService("test-key")

        result = service.create_table_summary_text("temp", "", "data (json)")

        expected = "Table: temp | Schema: data (json)"
        assert result == expected

    @patch("sq3m.infrastructure.llm.embedding_service.OpenAI")
    def test_generate_table_summary_embedding_success(self, mock_openai):
        """Test generating embedding for table summary."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3, 0.4])]
        mock_client.embeddings.create.return_value = mock_response

        service = EmbeddingService("test-key")

        table_summary = TableSummary(
            table_name="users", summary="Users table with user information"
        )

        result = service.generate_table_summary_embedding(table_summary)

        assert result.embedding == [0.1, 0.2, 0.3, 0.4]
        assert result.table_name == "users"
        assert result.summary == "Users table with user information"

        mock_client.embeddings.create.assert_called_once_with(
            input="Users table with user information", model="text-embedding-3-small"
        )

    @patch("sq3m.infrastructure.llm.embedding_service.OpenAI")
    def test_generate_table_summary_embedding_failure(self, mock_openai):
        """Test embedding generation failure for table summary."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_client.embeddings.create.side_effect = Exception("API Error")

        service = EmbeddingService("test-key")
        table_summary = TableSummary("test", "test summary")

        with pytest.raises(
            EmbeddingServiceError,
            match="Unexpected error during embedding generation: API Error",
        ):
            service.generate_table_summary_embedding(table_summary)

    def test_custom_model_initialization(self):
        """Test EmbeddingService with custom model."""
        with patch("sq3m.infrastructure.llm.embedding_service.OpenAI"):
            service = EmbeddingService("test-key", "text-embedding-ada-002")
            assert service.model == "text-embedding-ada-002"
