from __future__ import annotations

from typing import Any

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax
from rich.table import Table

from sq3m.application.services.database_service import DatabaseService
from sq3m.config.settings import Settings
from sq3m.domain.entities.database import DatabaseConnection, DatabaseType
from sq3m.infrastructure.llm.openai_service import OpenAIService


class CLI:
    def __init__(self) -> None:
        self.console = Console()
        self.settings = Settings()
        self.database_service: DatabaseService | None = None

    def run(self) -> None:
        self.console.print(
            Panel.fit(
                "🤖 SQ3M - AI-Powered Database Query Assistant", style="bold blue"
            )
        )

        # Initialize LLM service
        if not self._setup_llm():
            return

        # Setup database connection
        if not self._setup_database():
            return

        # Start interactive session
        self._start_interactive_session()

    def _setup_llm(self) -> bool:
        self.console.print("\n📋 Setting up LLM service...")

        api_key = self.settings.openai_api_key
        if not api_key:
            api_key = Prompt.ask("Enter your OpenAI API key")
            if not api_key:
                self.console.print("❌ OpenAI API key is required", style="red")
                return False

        model = self.settings.openai_model
        self.console.print(f"Using model: {model}", style="dim")

        try:
            llm_service = OpenAIService(api_key, model)
            self.database_service = DatabaseService(
                llm_service, api_key
            )  # Pass API key for hybrid search
            self.console.print("✅ LLM service initialized", style="green")
            return True
        except Exception as e:
            self.console.print(f"❌ Failed to initialize LLM service: {e}", style="red")
            return False

    def _setup_database(self) -> bool:
        self.console.print("\n🗄️ Setting up database connection...")

        # Check if configuration exists in environment
        connection: DatabaseConnection | None = None
        if self.settings.validate_db_config():
            # These should be validated by validate_db_config()
            assert self.settings.db_host is not None
            assert self.settings.db_port is not None
            assert self.settings.db_name is not None
            assert self.settings.db_username is not None
            assert self.settings.db_password is not None
            assert self.settings.db_type is not None

            connection = DatabaseConnection(
                host=self.settings.db_host,
                port=self.settings.db_port,
                database=self.settings.db_name,
                username=self.settings.db_username,
                password=self.settings.db_password,
                database_type=self.settings.db_type,
            )
        else:
            connection = self._prompt_database_connection()

        if connection is None:
            return False

        # Ensure database_service is initialized
        if self.database_service is None:
            self.console.print("❌ Database service not initialized", style="red")
            return False

        # Test and establish connection
        self.console.print(
            f"Connecting to {connection.database_type.value} database...", style="dim"
        )

        if not self.database_service.connect_to_database(connection):
            self.console.print("❌ Failed to connect to database", style="red")
            return False

        self.console.print("✅ Database connection established", style="green")

        # Analyze database schema
        self.console.print("🔍 Analyzing database schema...", style="dim")
        try:
            purposes = self.database_service.analyze_database_schema()
            self.console.print(f"✅ Analyzed {len(purposes)} tables", style="green")

            # Show table purposes
            if Confirm.ask("Show table analysis results?", default=False):
                self._display_table_purposes(purposes)

            return True
        except Exception as e:
            self.console.print(f"❌ Failed to analyze schema: {e}", style="red")
            return False

    def _prompt_database_connection(self) -> DatabaseConnection | None:
        # Database type selection
        db_types = ["mysql", "postgresql"]
        self.console.print("Available database types:")
        for i, db_type_name in enumerate(db_types, 1):
            self.console.print(f"  {i}. {db_type_name.upper()}")

        choice = Prompt.ask("Select database type", choices=["1", "2"])
        db_type_str = db_types[int(choice) - 1]

        selected_db_type: DatabaseType
        if db_type_str == "mysql":
            selected_db_type = DatabaseType.MYSQL
        elif db_type_str == "postgresql":
            selected_db_type = DatabaseType.POSTGRESQL
        else:
            self.console.print(
                f"❌ Unsupported database type: {db_type_str}", style="red"
            )
            return None

        # Connection details
        host = Prompt.ask("Database host", default="localhost")

        default_port = {"mysql": 3306, "postgresql": 5432}[db_type_str]
        port = Prompt.ask("Database port", default=str(default_port))

        database = Prompt.ask("Database name")
        username = Prompt.ask("Username")
        password = Prompt.ask("Password", password=True)

        try:
            return DatabaseConnection(
                host=host,
                port=int(port),
                database=database,
                username=username,
                password=password,
                database_type=selected_db_type,
            )
        except ValueError:
            self.console.print("❌ Invalid port number", style="red")
            return None

    def _display_table_purposes(self, purposes: dict[str, str]) -> None:
        table = Table(title="📊 Database Table Analysis")
        table.add_column("Table Name", style="cyan", no_wrap=True)
        table.add_column("Purpose", style="green")

        for table_name, purpose in purposes.items():
            table.add_row(table_name, purpose)

        self.console.print(table)

    def _start_interactive_session(self) -> None:
        self.console.print(
            Panel.fit("🚀 Interactive Query Session Started", style="bold green")
        )
        self.console.print(
            "Type your questions in natural language. Type 'quit' or 'exit' to stop.\n"
        )

        while True:
            try:
                query = Prompt.ask("🤔 What would you like to know")

                if query.lower() in ["quit", "exit", "q"]:
                    break

                if query.lower() in ["help", "h"]:
                    self._show_help()
                    continue

                if query.lower().startswith("tables"):
                    self._show_tables()
                    continue

                # Generate and execute SQL
                self._process_natural_language_query(query)

            except KeyboardInterrupt:
                break
            except Exception as e:
                self.console.print(f"❌ Error: {e}", style="red")

        self._cleanup()

    def _show_help(self) -> None:
        help_text = """
Available commands:
• Type any natural language query to generate SQL
• 'tables' - Show all database tables
• 'help' or 'h' - Show this help message
• 'quit', 'exit', or 'q' - Exit the application

Example queries:
• "Show all users"
• "Find orders from last month"
• "Count products by category"
• "Show user details for user ID 123"
        """
        self.console.print(Panel(help_text, title="Help", border_style="blue"))

    def _show_tables(self) -> None:
        if self.database_service is None:
            self.console.print("❌ Database service not initialized", style="red")
            return
        tables = self.database_service.get_tables()

        table_display = Table(title="📋 Database Tables")
        table_display.add_column("Table", style="cyan", no_wrap=True)
        table_display.add_column("Columns", style="white")
        table_display.add_column("Purpose", style="green")

        for table in tables:
            columns_str = f"{len(table.columns)} columns"
            purpose = table.purpose or "Not analyzed"
            table_display.add_row(table.name, columns_str, purpose)

        self.console.print(table_display)

    def _process_natural_language_query(self, query: str) -> None:
        self.console.print(f"🤖 Processing: {query}", style="dim")

        if self.database_service is None:
            self.console.print("❌ Database service not initialized", style="red")
            return

        try:
            sql_query, results = self.database_service.generate_and_execute_query(query)

            # Display generated SQL
            if sql_query.sql:
                self.console.print("\n📝 Generated SQL:")
                syntax = Syntax(
                    sql_query.sql, "sql", theme="monokai", line_numbers=True
                )
                self.console.print(syntax)

                if sql_query.explanation:
                    self.console.print(
                        f"\n💡 Explanation: {sql_query.explanation}", style="dim"
                    )

                if sql_query.confidence:
                    confidence_color = (
                        "green"
                        if sql_query.confidence > 0.7
                        else "yellow"
                        if sql_query.confidence > 0.4
                        else "red"
                    )
                    self.console.print(
                        f"🎯 Confidence: {sql_query.confidence:.1%}",
                        style=confidence_color,
                    )

            # Display results
            if results:
                if "error" in results[0]:
                    self.console.print(
                        f"\n❌ Query Error: {results[0]['error']}", style="red"
                    )
                else:
                    self._display_query_results(results)
            else:
                self.console.print(
                    "\n✅ Query executed successfully (no results)", style="green"
                )

        except Exception as e:
            self.console.print(f"\n❌ Error processing query: {e}", style="red")

    def _display_query_results(self, results: list[dict[str, Any]]) -> None:
        if not results:
            return

        self.console.print(f"\n📊 Results ({len(results)} rows):")

        # Create table for results
        result_table = Table()

        # Add columns
        if results:
            for column in results[0]:
                result_table.add_column(str(column), style="cyan")

            # Add rows (limit to first 20 for readability)
            for row in results[:20]:
                result_table.add_row(
                    *[
                        str(value) if value is not None else "NULL"
                        for value in row.values()
                    ]
                )

        self.console.print(result_table)

        if len(results) > 20:
            self.console.print(
                f"\n... showing first 20 of {len(results)} rows", style="dim"
            )

    def _cleanup(self) -> None:
        self.console.print("\n👋 Goodbye!")
        if self.database_service:
            self.database_service.disconnect()


@click.command()  # type: ignore[misc]
def main() -> None:
    cli = CLI()
    cli.run()


if __name__ == "__main__":
    main()
