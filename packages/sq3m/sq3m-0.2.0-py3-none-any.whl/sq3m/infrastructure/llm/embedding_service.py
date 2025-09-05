from __future__ import annotations

from typing import TYPE_CHECKING

from openai import APIConnectionError, APIError, OpenAI, RateLimitError

if TYPE_CHECKING:
    from sq3m.domain.entities.table_summary import TableSummary


class EmbeddingServiceError(Exception):
    """Custom exception for embedding service errors."""

    pass


class EmbeddingService:
    """Service for generating embeddings using OpenAI's API."""

    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate_embedding(self, text: str) -> list[float]:
        """
        Generate embedding vector for a given text.

        Raises:
            EmbeddingServiceError: When OpenAI API fails with non-200 response
        """
        try:
            response = self.client.embeddings.create(input=text, model=self.model)
            return response.data[0].embedding
        except APIError as e:
            error_msg = f"OpenAI API error: {e}"
            print(f"❌ {error_msg}")
            raise EmbeddingServiceError(error_msg)
        except RateLimitError as e:
            error_msg = f"OpenAI rate limit exceeded: {e}"
            print(f"❌ {error_msg}")
            raise EmbeddingServiceError(error_msg)
        except APIConnectionError as e:
            error_msg = f"Failed to connect to OpenAI API: {e}"
            print(f"❌ {error_msg}")
            raise EmbeddingServiceError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error during embedding generation: {str(e)}"
            print(f"❌ {error_msg}")
            raise EmbeddingServiceError(error_msg)

    def generate_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embedding vectors for multiple texts.

        Raises:
            EmbeddingServiceError: When OpenAI API fails with non-200 response
        """
        try:
            response = self.client.embeddings.create(input=texts, model=self.model)
            return [data.embedding for data in response.data]
        except APIError as e:
            error_msg = f"OpenAI API error: {e}"
            print(f"❌ {error_msg}")
            raise EmbeddingServiceError(error_msg)
        except RateLimitError as e:
            error_msg = f"OpenAI rate limit exceeded: {e}"
            print(f"❌ {error_msg}")
            raise EmbeddingServiceError(error_msg)
        except APIConnectionError as e:
            error_msg = f"Failed to connect to OpenAI API: {e}"
            print(f"❌ {error_msg}")
            raise EmbeddingServiceError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error during batch embedding generation: {str(e)}"
            print(f"❌ {error_msg}")
            raise EmbeddingServiceError(error_msg)

    def create_table_summary_text(
        self, table_name: str, purpose: str, schema_info: str
    ) -> str:
        """Create a comprehensive text representation of a table for embedding."""
        text_parts = [f"Table: {table_name}"]

        if purpose:
            text_parts.append(f"Purpose: {purpose}")

        text_parts.append(f"Schema: {schema_info}")

        return " | ".join(text_parts)

    def generate_table_summary_embedding(
        self, table_summary: TableSummary
    ) -> TableSummary:
        """Generate and attach embedding to a table summary."""
        embedding = self.generate_embedding(table_summary.summary)
        table_summary.embedding = embedding
        return table_summary
