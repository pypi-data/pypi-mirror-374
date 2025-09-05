from __future__ import annotations

import json
import math
import sqlite3

from sq3m.domain.entities.table_summary import SearchResult, TableSummary
from sq3m.domain.interfaces.table_search_repository import TableSearchRepository


class SQLiteTableSearchRepository(TableSearchRepository):
    """SQLite-based implementation of table search repository with hybrid search capabilities."""

    def __init__(self, db_path: str = "table_search.db"):
        self.db_path = db_path
        self.connection: sqlite3.Connection | None = None

    def _get_connection(self) -> sqlite3.Connection:
        """Get or create database connection."""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
        return self.connection

    def initialize_storage(self) -> None:
        """Initialize the storage tables and indexes."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Create table summaries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS table_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT NOT NULL UNIQUE,
                summary TEXT NOT NULL,
                purpose TEXT,
                embedding TEXT,  -- JSON-encoded embedding vector
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create FTS5 virtual table for full-text search
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS table_summaries_fts USING fts5(
                table_name,
                summary,
                purpose,
                content='table_summaries',
                content_rowid='id'
            )
        """)

        # Create triggers to keep FTS table in sync
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS table_summaries_ai AFTER INSERT ON table_summaries BEGIN
                INSERT INTO table_summaries_fts(rowid, table_name, summary, purpose)
                VALUES (new.id, new.table_name, new.summary, new.purpose);
            END
        """)

        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS table_summaries_ad AFTER DELETE ON table_summaries BEGIN
                INSERT INTO table_summaries_fts(table_summaries_fts, rowid, table_name, summary, purpose)
                VALUES ('delete', old.id, old.table_name, old.summary, old.purpose);
            END
        """)

        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS table_summaries_au AFTER UPDATE ON table_summaries BEGIN
                INSERT INTO table_summaries_fts(table_summaries_fts, rowid, table_name, summary, purpose)
                VALUES ('delete', old.id, old.table_name, old.summary, old.purpose);
                INSERT INTO table_summaries_fts(rowid, table_name, summary, purpose)
                VALUES (new.id, new.table_name, new.summary, new.purpose);
            END
        """)

        conn.commit()

    def store_table_summary(self, table_summary: TableSummary) -> None:
        """Store a single table summary."""
        conn = self._get_connection()
        cursor = conn.cursor()

        embedding_json = (
            json.dumps(table_summary.embedding) if table_summary.embedding else None
        )

        cursor.execute(
            """
            INSERT OR REPLACE INTO table_summaries
            (table_name, summary, purpose, embedding, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """,
            (
                table_summary.table_name,
                table_summary.summary,
                table_summary.purpose,
                embedding_json,
            ),
        )

        conn.commit()

    def store_table_summaries(self, table_summaries: list[TableSummary]) -> None:
        """Store multiple table summaries."""
        conn = self._get_connection()
        cursor = conn.cursor()

        data = []
        for ts in table_summaries:
            embedding_json = json.dumps(ts.embedding) if ts.embedding else None
            data.append((ts.table_name, ts.summary, ts.purpose, embedding_json))

        cursor.executemany(
            """
            INSERT OR REPLACE INTO table_summaries
            (table_name, summary, purpose, embedding, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """,
            data,
        )

        conn.commit()

    def _cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2, strict=False))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))

        if magnitude1 == 0.0 or magnitude2 == 0.0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def search_tables_vector(
        self, query_embedding: list[float], limit: int = 10
    ) -> list[SearchResult]:
        """Search tables using vector similarity only."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT table_name, summary, purpose, embedding
            FROM table_summaries
            WHERE embedding IS NOT NULL
        """)

        results = []
        for row in cursor.fetchall():
            try:
                stored_embedding = json.loads(row["embedding"])
                similarity = self._cosine_similarity(query_embedding, stored_embedding)

                table_summary = TableSummary(
                    table_name=row["table_name"],
                    summary=row["summary"],
                    purpose=row["purpose"],
                    embedding=stored_embedding,
                )

                results.append(
                    SearchResult(
                        table_summary=table_summary,
                        score=similarity,
                        search_type="vector",
                    )
                )
            except (json.JSONDecodeError, TypeError):
                continue

        # Sort by similarity score (descending)
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:limit]

    def search_tables_keyword(self, query: str, limit: int = 10) -> list[SearchResult]:
        """Search tables using keyword/full-text search only."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Sanitize query for FTS5 by escaping special characters and extracting keywords
        sanitized_query = self._sanitize_fts5_query(query)

        try:
            # Use FTS5 MATCH for full-text search
            cursor.execute(
                """
                SELECT ts.table_name, ts.summary, ts.purpose, ts.embedding,
                       fts.rank as relevance_score
                FROM table_summaries_fts fts
                JOIN table_summaries ts ON ts.id = fts.rowid
                WHERE table_summaries_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            """,
                (sanitized_query, limit),
            )
        except Exception as e:
            print(f"FTS5 search failed with query '{sanitized_query}': {e}")
            # Fallback to LIKE search if FTS5 fails
            return self._fallback_keyword_search(query, limit)

        results = []
        for row in cursor.fetchall():
            try:
                embedding = json.loads(row["embedding"]) if row["embedding"] else None
            except (json.JSONDecodeError, TypeError):
                embedding = None

            table_summary = TableSummary(
                table_name=row["table_name"],
                summary=row["summary"],
                purpose=row["purpose"],
                embedding=embedding,
            )

            # Convert SQLite FTS rank to positive score (FTS ranks are negative)
            score = (
                abs(float(row["relevance_score"])) if row["relevance_score"] else 0.0
            )

            results.append(
                SearchResult(
                    table_summary=table_summary, score=score, search_type="keyword"
                )
            )

        return results

    def _sanitize_fts5_query(self, query: str) -> str:
        """Sanitize query string for FTS5 by extracting keywords and escaping special characters."""
        import re

        # Extract English and Korean words, numbers
        # Remove special FTS5 operators and punctuation
        words = re.findall(r"\b[a-zA-Z가-힣]\w*\b", query)

        if not words:
            # If no words found, try to extract any alphanumeric sequences
            words = re.findall(r"[a-zA-Z가-힣0-9]+", query)

        if not words:
            # Last resort: use original query but escape quotes
            return query.replace('"', '""').replace("'", "''")

        # Join words with OR to make the search more flexible
        return " OR ".join(
            [f'"{word}"' for word in words[:10]]
        )  # Limit to first 10 words

    def _fallback_keyword_search(self, query: str, limit: int) -> list[SearchResult]:
        """Fallback search using LIKE when FTS5 fails."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Extract keywords for LIKE search
        import re

        keywords = re.findall(r"\b[a-zA-Z가-힣]\w*\b", query.lower())

        if not keywords:
            return []

        # Build LIKE conditions for multiple keywords
        like_conditions = []
        params = []

        for keyword in keywords[:5]:  # Limit to first 5 keywords
            like_conditions.append(
                "(LOWER(ts.table_name) LIKE ? OR LOWER(ts.summary) LIKE ? OR LOWER(ts.purpose) LIKE ?)"
            )
            params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])

        where_clause = " OR ".join(like_conditions)
        params.append(str(limit))

        cursor.execute(
            f"""
            SELECT DISTINCT ts.table_name, ts.summary, ts.purpose, ts.embedding,
                   1.0 as relevance_score
            FROM table_summaries ts
            WHERE {where_clause}
            ORDER BY ts.table_name
            LIMIT ?
        """,
            params,
        )

        results = []
        for row in cursor.fetchall():
            try:
                embedding = json.loads(row["embedding"]) if row["embedding"] else None
            except (json.JSONDecodeError, TypeError):
                embedding = None

            table_summary = TableSummary(
                table_name=row["table_name"],
                summary=row["summary"],
                purpose=row["purpose"],
                embedding=embedding,
            )

            results.append(
                SearchResult(
                    table_summary=table_summary,
                    score=1.0,  # Default score for LIKE search
                    search_type="keyword_fallback",
                )
            )

        return results

    def _reciprocal_rank_fusion(
        self,
        vector_results: list[SearchResult],
        keyword_results: list[SearchResult],
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3,
        k: int = 60,  # RRF parameter
    ) -> list[SearchResult]:
        """Combine search results using Reciprocal Rank Fusion."""

        # Create maps for quick lookup
        vector_map = {
            result.table_summary.table_name: (i, result)
            for i, result in enumerate(vector_results)
        }
        keyword_map = {
            result.table_summary.table_name: (i, result)
            for i, result in enumerate(keyword_results)
        }

        # Get all unique table names
        all_tables = set(vector_map.keys()) | set(keyword_map.keys())

        combined_results = []

        for table_name in all_tables:
            vector_rank, vector_result = vector_map.get(
                table_name, (len(vector_results), None)
            )
            keyword_rank, keyword_result = keyword_map.get(
                table_name, (len(keyword_results), None)
            )

            # Calculate RRF score
            vector_rrf = vector_weight / (k + vector_rank + 1)
            keyword_rrf = keyword_weight / (k + keyword_rank + 1)
            rrf_score = vector_rrf + keyword_rrf

            # Use the result with better individual score, or vector result as default
            result = (
                vector_result
                if vector_result
                and (not keyword_result or vector_result.score >= keyword_result.score)
                else keyword_result
            )

            if result:
                combined_results.append(
                    SearchResult(
                        table_summary=result.table_summary,
                        score=rrf_score,
                        search_type="hybrid",
                    )
                )

        # Sort by RRF score (descending)
        combined_results.sort(key=lambda x: x.score, reverse=True)
        return combined_results

    def search_tables_hybrid(
        self,
        query: str,
        query_embedding: list[float],
        limit: int = 10,
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3,
    ) -> list[SearchResult]:
        """
        Perform hybrid search using both vector similarity and keyword search.
        Uses Reciprocal Rank Fusion to combine results.
        """
        # Get results from both search methods
        vector_results = self.search_tables_vector(
            query_embedding, limit * 2
        )  # Get more candidates
        keyword_results = self.search_tables_keyword(query, limit * 2)

        # Combine using RRF
        hybrid_results = self._reciprocal_rank_fusion(
            vector_results, keyword_results, vector_weight, keyword_weight
        )

        return hybrid_results[:limit]

    def get_all_table_summaries(self) -> list[TableSummary]:
        """Get all stored table summaries."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT table_name, summary, purpose, embedding
            FROM table_summaries
            ORDER BY table_name
        """)

        results = []
        for row in cursor.fetchall():
            try:
                embedding = json.loads(row["embedding"]) if row["embedding"] else None
            except (json.JSONDecodeError, TypeError):
                embedding = None

            results.append(
                TableSummary(
                    table_name=row["table_name"],
                    summary=row["summary"],
                    purpose=row["purpose"],
                    embedding=embedding,
                )
            )

        return results

    def clear_table_summaries(self) -> None:
        """Clear all stored table summaries."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM table_summaries")
        conn.commit()

    def __del__(self) -> None:
        """Close database connection when object is destroyed."""
        if self.connection:
            self.connection.close()
