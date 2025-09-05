"""Simple tests for embedding service error handling."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from sq3m.infrastructure.llm.embedding_service import (
    EmbeddingService,
    EmbeddingServiceError,
)


class TestEmbeddingServiceErrorHandlingSimple:
    """Simple test cases for embedding service error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.api_key = "test-api-key"

    @patch("sq3m.infrastructure.llm.embedding_service.OpenAI")
    def test_generic_exception_handling(self, mock_openai):
        """Test handling of generic exceptions."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_client.embeddings.create.side_effect = ValueError("Some unexpected error")

        service = EmbeddingService(self.api_key)

        with pytest.raises(
            EmbeddingServiceError, match="Unexpected error during embedding generation"
        ):
            service.generate_embedding("test text")

    @patch("sq3m.infrastructure.llm.embedding_service.OpenAI")
    def test_batch_generic_exception_handling(self, mock_openai):
        """Test handling of generic exceptions in batch operations."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_client.embeddings.create.side_effect = RuntimeError(
            "Unexpected batch error"
        )

        service = EmbeddingService(self.api_key)

        with pytest.raises(
            EmbeddingServiceError,
            match="Unexpected error during batch embedding generation",
        ):
            service.generate_embeddings_batch(["text1", "text2"])

    @patch("sq3m.infrastructure.llm.embedding_service.OpenAI")
    def test_successful_embedding_generation(self, mock_openai):
        """Test that successful API calls work normally."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3])]
        mock_client.embeddings.create.return_value = mock_response

        service = EmbeddingService(self.api_key)
        result = service.generate_embedding("test text")

        assert result == [0.1, 0.2, 0.3]

    @patch("sq3m.infrastructure.llm.embedding_service.OpenAI")
    def test_successful_batch_embedding_generation(self, mock_openai):
        """Test that successful batch API calls work normally."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_response.data = [
            Mock(embedding=[0.1, 0.2, 0.3]),
            Mock(embedding=[0.4, 0.5, 0.6]),
        ]
        mock_client.embeddings.create.return_value = mock_response

        service = EmbeddingService(self.api_key)
        result = service.generate_embeddings_batch(["text1", "text2"])

        expected = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        assert result == expected

    def test_embedding_service_error_inheritance(self):
        """Test that EmbeddingServiceError is properly defined."""
        error = EmbeddingServiceError("Test error")
        assert isinstance(error, Exception)
        assert str(error) == "Test error"

    @patch("sq3m.infrastructure.llm.embedding_service.OpenAI")
    @patch("builtins.print")
    def test_error_message_printing(self, mock_print, mock_openai):
        """Test that error messages are printed before raising exceptions."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_client.embeddings.create.side_effect = ValueError("Test error")

        service = EmbeddingService(self.api_key)

        with pytest.raises(EmbeddingServiceError):
            service.generate_embedding("test text")

        # Verify error message was printed
        mock_print.assert_called_once()
        printed_message = mock_print.call_args[0][0]
        assert "❌" in printed_message
        assert "Unexpected error during embedding generation" in printed_message
