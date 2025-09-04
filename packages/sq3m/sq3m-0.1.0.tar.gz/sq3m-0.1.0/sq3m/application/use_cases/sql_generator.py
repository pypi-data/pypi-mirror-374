from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

from sq3m.domain.entities.database import SQLQuery, Table
from sq3m.infrastructure.history.markdown_history import MarkdownHistory

if TYPE_CHECKING:
    from sq3m.domain.interfaces.database_repository import DatabaseRepository
    from sq3m.domain.interfaces.llm_service import LLMService


class SQLGenerator:
    def __init__(
        self,
        database_repository: DatabaseRepository,
        llm_service: LLMService,
        history: MarkdownHistory | None = None,
    ):
        self.database_repository = database_repository
        self.llm_service = llm_service
        self.history = history or MarkdownHistory()

    def generate_sql(self, natural_language: str, tables: list[Table]) -> SQLQuery:
        return self.llm_service.generate_sql(natural_language, tables)

    def execute_sql(self, sql: str) -> list[dict[str, Any]]:
        return self.database_repository.execute_query(sql)

    def generate_and_execute(
        self, natural_language: str, tables: list[Table], max_retries: int = 2
    ) -> tuple[SQLQuery, list[dict[str, Any]]]:
        """
        Generate SQL query and execute it with retry logic on failure.

        Args:
            natural_language: The natural language query
            tables: List of available tables
            max_retries: Maximum number of retry attempts (default: 2)

        Returns:
            Tuple of (final_sql_query, results)
        """
        attempt = 0
        sql_query = None
        last_error = None

        while attempt <= max_retries:
            # Generate SQL query
            if attempt == 0:
                # First attempt: normal generation
                sql_query = self.generate_sql(natural_language, tables)
            else:
                # Retry attempt: use error feedback
                if sql_query is not None and sql_query.sql:
                    sql_query = self.llm_service.generate_sql_with_error_feedback(
                        natural_language, tables, sql_query.sql, str(last_error)
                    )
                else:
                    # Cannot retry without previous SQL
                    break

            # Skip execution if SQL is invalid or error comment
            if not sql_query.sql or sql_query.sql.startswith("--"):
                return sql_query, []

            try:
                # Try to execute the SQL
                results = self.execute_sql(sql_query.sql)

                # Log successful execution to history
                self._log_to_history(natural_language, sql_query, results, attempt)

                return sql_query, results

            except Exception as e:
                last_error = e
                attempt += 1

                # If this was the last attempt, break
                if attempt > max_retries:
                    break

        # If we get here, all attempts failed
        # Return the last query attempt (or create a fallback if None)
        if sql_query is None:
            sql_query = SQLQuery(
                natural_language=natural_language,
                sql="-- Failed to generate SQL",
                explanation="Failed to generate any SQL query",
                confidence=0.0,
            )

        results = [
            {
                "error": f"Query failed after {max_retries + 1} attempts. Last error: {str(last_error)}"
            }
        ]

        # Log to history
        self._log_to_history(natural_language, sql_query, results, max_retries)

        return sql_query, results

    def _log_to_history(
        self,
        natural_language: str,
        sql_query: SQLQuery,
        results: list[dict[str, Any]],
        retry_count: int = 0,
    ) -> None:
        """Log query and response to history (async wrapper)."""
        try:
            # Format execution result
            if results and isinstance(results, list):
                if len(results) == 1 and "error" in results[0]:
                    execution_result = f"Error: {results[0]['error']}"
                else:
                    execution_result = f"Success: {len(results)} rows returned"
                    if len(results) <= 5:  # Show sample for small results
                        execution_result += f"\nSample: {results[:3]}"
            else:
                execution_result = "No results"

            # Run async history logging - use asyncio.run for simplicity
            asyncio.run(
                self.history.add_query_and_response(
                    user_query=natural_language,
                    sql=sql_query.sql,
                    explanation=sql_query.explanation or "",
                    confidence=sql_query.confidence or 0.0,
                    execution_result=execution_result,
                    retry_count=retry_count,
                )
            )
        except Exception:
            # Don't let history logging break the main flow
            pass
