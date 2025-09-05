from __future__ import annotations

import json
from typing import Any

from openai import AsyncOpenAI, OpenAI

from sq3m.domain.entities.database import SQLQuery, Table
from sq3m.domain.interfaces.llm_service import LLMService
from sq3m.infrastructure.prompts.prompt_loader import PromptLoader


class OpenAIService(LLMService):
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-3.5-turbo",
        base_url: str | None = None,
        system_prompt_path: str | None = None,
    ):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.async_client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = model

        # Load system prompt from file
        self.prompt_loader = PromptLoader()
        self.system_prompt = self._load_system_prompt(system_prompt_path)

    def _load_system_prompt(self, custom_path: str | None = None) -> str:
        """Load system prompt from file with error handling."""
        try:
            return self.prompt_loader.load_system_prompt(custom_path)
        except Exception as e:
            print(f"Warning: Failed to load system prompt: {e}")
            # Fallback to a basic prompt
            return """You are a database expert who analyzes table schemas and generates SQL queries.
You have deep understanding of relational database design patterns and can infer table purposes from their structure and sample data.
Always provide accurate, efficient SQL queries and clear explanations."""

    def reload_system_prompt(self, custom_path: str | None = None) -> str:
        """Reload system prompt from file and return the new content."""
        self.system_prompt = self._load_system_prompt(custom_path)
        return self.system_prompt

    def get_current_system_prompt(self) -> str:
        """Get the currently loaded system prompt."""
        return self.system_prompt

    def get_prompt_info(self) -> dict[str, Any]:
        """Get information about the current prompt configuration."""
        return self.prompt_loader.get_available_prompts()

    def _build_table_description(self, table: Table) -> str:
        columns_info: list[str] = []
        for col in table.columns:
            col_info = f"- {col.name} ({col.data_type})"
            if col.is_primary_key:
                col_info += " [PRIMARY KEY]"
            if col.comment:
                col_info += f" - {col.comment}"
            columns_info.append(col_info)

        table_description = f"Table: {table.name}\n"
        if table.comment:
            table_description += f"Description: {table.comment}\n"
        table_description += "Columns:\n" + "\n".join(columns_info)

        # Add sample data if available
        if table.sample_rows:
            table_description += "\n\nSample Data:\n"
            for i, row in enumerate(table.sample_rows[:3]):  # Show max 3 rows
                row_str = ", ".join([f"{k}: {v}" for k, v in row.items()])
                table_description += f"Row {i + 1}: {row_str}\n"

        return table_description

    def infer_table_purpose(self, table: Table) -> str:
        table_description = self._build_table_description(table)

        prompt = f"""
        Based on the following database table schema and sample data, infer what this table is used for and describe its purpose in 1-2 sentences:

        {table_description}

        Please provide a clear, concise description of the table's purpose and what kind of data it stores.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt},
                ],
            )

            content = response.choices[0].message.content
            return str(content).strip() if content else ""
        except Exception as e:
            return f"Could not infer purpose for table {table.name}: {str(e)}"

    async def infer_table_purpose_async(self, table: Table) -> str:
        table_description = self._build_table_description(table)

        prompt = f"""
        Based on the following database table schema and sample data, infer what this table is used for and describe its purpose in 1-2 sentences:

        {table_description}

        Please provide a clear, concise description of the table's purpose and what kind of data it stores.
        """

        try:
            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt},
                ],
            )

            content = response.choices[0].message.content
            return str(content).strip() if content else ""
        except Exception as e:
            return f"Could not infer purpose for table {table.name}: {str(e)}"

    def generate_sql(
        self,
        natural_language: str,
        tables: list[Table],
        conversation_history: str | None = None,
    ) -> SQLQuery:
        schema_info: list[str] = []
        for table in tables:
            table_info = f"\n{'=' * 50}\nTable: {table.name}"
            if table.purpose:
                table_info += f"\nPurpose: {table.purpose}"
            if table.comment:
                table_info += f"\nDescription: {table.comment}"

            # Add table-level information
            if hasattr(table, "row_count") and table.row_count is not None:
                table_info += f"\nEstimated Rows: {table.row_count:,}"

            table_info += f"\n\nColumns ({len(table.columns)} total):"
            for col in table.columns:
                col_info = f"\n  • {col.name}"

                # Data type with more details
                col_info += f" ({col.data_type})"

                # Constraints and properties
                properties: list[str] = []
                if col.is_primary_key:
                    properties.append("PRIMARY KEY")
                if not col.is_nullable:
                    properties.append("NOT NULL")
                if hasattr(col, "is_unique") and col.is_unique:
                    properties.append("UNIQUE")
                if hasattr(col, "is_auto_increment") and col.is_auto_increment:
                    properties.append("AUTO_INCREMENT")
                if hasattr(col, "default_value") and col.default_value is not None:
                    properties.append(f"DEFAULT '{col.default_value}'")

                if properties:
                    col_info += f" [{', '.join(properties)}]"

                # Foreign key relationships
                if hasattr(col, "foreign_key") and col.foreign_key:
                    col_info += f"\n    └─ REFERENCES {col.foreign_key}"
                elif hasattr(col, "references") and col.references:
                    col_info += f"\n    └─ REFERENCES {col.references}"

                # Column description/comment
                if col.comment:
                    col_info += f"\n    └─ {col.comment}"

                table_info += col_info

            # Add indexes information if available
            if hasattr(table, "indexes") and table.indexes:
                table_info += f"\n\nIndexes ({len(table.indexes)} total):"
                for idx in table.indexes:
                    idx_name = getattr(idx, "name", "unnamed_index")
                    idx_columns = getattr(idx, "columns", [])
                    idx_type = getattr(idx, "type", "BTREE")
                    is_unique = getattr(idx, "is_unique", False)

                    idx_info = f"\n  • {idx_name} ({idx_type})"
                    if is_unique:
                        idx_info += " [UNIQUE]"
                    if idx_columns:
                        idx_info += f" ON ({', '.join(idx_columns)})"
                    table_info += idx_info

            # Enhanced sample data with column headers
            if table.sample_rows:
                table_info += f"\n\nSample Data ({len(table.sample_rows)} rows shown):"

                # Get column names for header
                if table.sample_rows:
                    column_names: list[str] = list(table.sample_rows[0].keys())
                    # Create header
                    header = " | ".join([f"{col:>12}" for col in column_names])
                    separator = "-" * len(header)
                    table_info += f"\n{header}\n{separator}"

                    # Add data rows
                    for row in table.sample_rows[:10]:  # Show up to 10 rows
                        row_values: list[str] = []
                        for col_name in column_names:
                            value = row.get(col_name, "NULL")
                            # Format value for display
                            if value is None:
                                value = "NULL"
                            elif isinstance(value, str) and len(str(value)) > 12:
                                value = str(value)[:9] + "..."
                            row_values.append(f"{str(value):>12}")
                        table_info += f"\n{' | '.join(row_values)}"

            # Add relationship information if available
            if hasattr(table, "relationships") and table.relationships:
                table_info += "\n\nRelationships:"
                for rel in table.relationships:
                    rel_type = getattr(rel, "type", "UNKNOWN")
                    target_table = getattr(rel, "target_table", "unknown")
                    foreign_key = getattr(rel, "foreign_key", "unknown")
                    table_info += f"\n  • {rel_type} relationship with {target_table} via {foreign_key}"

            schema_info.append(table_info)

        schema_context = "\n".join(schema_info)

        # Enhanced prompt with conversation history
        prompt = f"""
        Given the following database schema, convert the natural language query to SQL:

        DATABASE SCHEMA:
        {schema_context}
        """

        # Add conversation history if available
        if conversation_history and conversation_history.strip():
            prompt += f"""

        PREVIOUS CONVERSATION CONTEXT:
        The user has been asking questions about this database. Here are the recent questions and responses to help you understand the context and provide better answers:

        {conversation_history}

        Based on this conversation history, please consider:
        1. Similar patterns or themes in the user's questions
        2. Previously discussed tables, columns, or business logic
        3. Any clarifications or corrections made in previous exchanges
        4. The user's apparent level of SQL knowledge and preferred explanation style
        """

        prompt += f"""

        CURRENT NATURAL LANGUAGE QUERY:
        {natural_language}

        Please provide:
        1. A valid SQL query that answers the natural language question
        2. A brief explanation of what the query does
        3. A confidence score (0-100) indicating how certain you are about the query

        When there's conversation history:
        - Reference previous queries or patterns when relevant
        - Build upon previously established understanding
        - Use consistent naming conventions and query styles from the conversation
        - If the current question seems related to previous ones, mention the connection

        Format your response as JSON:
        {{
            "sql": "SELECT ...",
            "explanation": "This query...",
            "confidence": 85
        }}
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt},
                ],
            )

            content = response.choices[0].message.content
            response_text = content.strip() if content else ""

            # Try to parse JSON response
            try:
                result = json.loads(response_text)
                return SQLQuery(
                    natural_language=natural_language,
                    sql=result.get("sql", ""),
                    explanation=result.get("explanation", ""),
                    confidence=result.get("confidence", 0) / 100.0,
                )
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return SQLQuery(
                    natural_language=natural_language,
                    sql=response_text,
                    explanation="Generated SQL query",
                    confidence=0.5,
                )

        except Exception as e:
            return SQLQuery(
                natural_language=natural_language,
                sql=f"-- Error generating SQL: {str(e)}",
                explanation=f"Failed to generate SQL: {str(e)}",
                confidence=0.0,
            )

    def generate_sql_with_error_feedback(
        self,
        natural_language: str,
        tables: list[Table],
        previous_sql: str,
        error_message: str,
    ) -> SQLQuery:
        schema_info: list[str] = []
        for table in tables:
            table_info = f"\nTable: {table.name}"
            if table.purpose:
                table_info += f"\nPurpose: {table.purpose}"
            if table.comment:
                table_info += f"\nDescription: {table.comment}"

            table_info += "\nColumns:"
            for col in table.columns:
                col_info = f"\n  - {col.name} ({col.data_type})"
                if col.is_primary_key:
                    col_info += " [PK]"
                if not col.is_nullable:
                    col_info += " [NOT NULL]"
                if col.comment:
                    col_info += f" - {col.comment}"
                table_info += col_info

            # Add sample data if available
            if table.sample_rows:
                table_info += "\n\nSample Data:"
                for i, row in enumerate(table.sample_rows[:2]):
                    row_str = ", ".join([f"{k}: {v}" for k, v in row.items()])
                    table_info += f"\n  Row {i + 1}: {row_str}"

            schema_info.append(table_info)

        schema_context = "\n".join(schema_info)

        prompt = f"""
        The previous SQL query failed to execute. Please analyze the error and generate a corrected SQL query.

        DATABASE SCHEMA:
        {schema_context}

        ORIGINAL NATURAL LANGUAGE QUERY:
        {natural_language}

        PREVIOUS SQL QUERY (FAILED):
        {previous_sql}

        ERROR MESSAGE:
        {error_message}

        Please provide:
        1. A corrected SQL query that fixes the error and answers the natural language question
        2. An explanation of what was wrong with the previous query and how you fixed it
        3. A confidence score (0-100) indicating how certain you are about the corrected query

        Common issues to check:
        - Column names that don't exist in the schema
        - Incorrect table names
        - Syntax errors (missing commas, parentheses, etc.)
        - JOIN conditions that reference non-existent relationships
        - Aggregate functions used incorrectly
        - Data type mismatches

        Format your response as JSON:
        {{
            "sql": "SELECT ...",
            "explanation": "The error was caused by... I fixed it by...",
            "confidence": 85
        }}
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt},
                ],
            )

            content = response.choices[0].message.content
            response_text = content.strip() if content else ""

            # Try to parse JSON response
            try:
                result = json.loads(response_text)
                return SQLQuery(
                    natural_language=natural_language,
                    sql=result.get("sql", ""),
                    explanation=result.get("explanation", ""),
                    confidence=result.get("confidence", 0) / 100.0,
                )
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return SQLQuery(
                    natural_language=natural_language,
                    sql=response_text,
                    explanation="Corrected SQL query based on error feedback",
                    confidence=0.4,
                )

        except Exception as e:
            return SQLQuery(
                natural_language=natural_language,
                sql=f"-- Error generating corrected SQL: {str(e)}",
                explanation=f"Failed to generate corrected SQL: {str(e)}",
                confidence=0.0,
            )

    async def generate_sql_async(
        self,
        natural_language: str,
        tables: list[Table],
        conversation_history: str | None = None,
    ) -> SQLQuery:
        schema_info: list[str] = []
        for table in tables:
            table_info = f"\nTable: {table.name}"
            if table.purpose:
                table_info += f"\nPurpose: {table.purpose}"
            if table.comment:
                table_info += f"\nDescription: {table.comment}"

            table_info += "\nColumns:"
            for col in table.columns:
                col_info = f"\n  - {col.name} ({col.data_type})"
                if col.is_primary_key:
                    col_info += " [PK]"
                if not col.is_nullable:
                    col_info += " [NOT NULL]"
                if col.comment:
                    col_info += f" - {col.comment}"
                table_info += col_info

            # Add sample data if available
            if table.sample_rows:
                table_info += "\n\nSample Data:"
                for i, row in enumerate(table.sample_rows[:2]):
                    row_str = ", ".join([f"{k}: {v}" for k, v in row.items()])
                    table_info += f"\n  Row {i + 1}: {row_str}"

            schema_info.append(table_info)

        schema_context = "\n".join(schema_info)

        # Enhanced prompt with conversation history (similar to sync method)
        prompt = f"""
        Given the following database schema, convert the natural language query to SQL:

        DATABASE SCHEMA:
        {schema_context}
        """

        # Add conversation history if available
        if conversation_history and conversation_history.strip():
            prompt += f"""

        PREVIOUS CONVERSATION CONTEXT:
        The user has been asking questions about this database. Here are the recent questions and responses to help you understand the context and provide better answers:

        {conversation_history}

        Based on this conversation history, please consider:
        1. Similar patterns or themes in the user's questions
        2. Previously discussed tables, columns, or business logic
        3. Any clarifications or corrections made in previous exchanges
        4. The user's apparent level of SQL knowledge and preferred explanation style
        """

        prompt += f"""

        CURRENT NATURAL LANGUAGE QUERY:
        {natural_language}

        Please provide:
        1. A valid SQL query that answers the natural language question
        2. A brief explanation of what the query does
        3. A confidence score (0-100) indicating how certain you are about the query

        When there's conversation history:
        - Reference previous queries or patterns when relevant
        - Build upon previously established understanding
        - Use consistent naming conventions and query styles from the conversation
        - If the current question seems related to previous ones, mention the connection

        Format your response as JSON:
        {{
            "sql": "SELECT ...",
            "explanation": "This query...",
            "confidence": 85
        }}
        """

        try:
            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt},
                ],
            )

            content = response.choices[0].message.content
            response_text = content.strip() if content else ""

            # Try to parse JSON response
            try:
                result = json.loads(response_text)
                return SQLQuery(
                    natural_language=natural_language,
                    sql=result.get("sql", ""),
                    explanation=result.get("explanation", ""),
                    confidence=result.get("confidence", 0) / 100.0,
                )
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return SQLQuery(
                    natural_language=natural_language,
                    sql=response_text,
                    explanation="Generated SQL query",
                    confidence=0.5,
                )

        except Exception as e:
            return SQLQuery(
                natural_language=natural_language,
                sql=f"-- Error generating SQL: {str(e)}",
                explanation=f"Failed to generate SQL: {str(e)}",
                confidence=0.0,
            )
