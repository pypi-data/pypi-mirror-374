from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class TableSummary:
    """Table summary entity for hybrid search storage."""

    table_name: str
    summary: str
    purpose: str | None = None
    embedding: list[float] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "table_name": self.table_name,
            "summary": self.summary,
            "purpose": self.purpose,
            "embedding": self.embedding,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TableSummary:
        """Create from dictionary."""
        return cls(
            table_name=data["table_name"],
            summary=data["summary"],
            purpose=data.get("purpose"),
            embedding=data.get("embedding"),
        )


@dataclass
class SearchResult:
    """Search result with relevance score."""

    table_summary: TableSummary
    score: float
    search_type: str  # "vector", "keyword", or "hybrid"
