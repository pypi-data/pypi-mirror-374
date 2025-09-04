from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import aiofiles


class MarkdownHistory:
    def __init__(self, history_dir: str = "."):
        self.history_dir = Path(history_dir)
        self.current_session_file: Path | None = None
        self.session_id: str | None = None

    def _get_session_filename(self, session_id: str) -> str:
        """Generate filename for a session."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_session_id = "".join(c for c in session_id if c.isalnum() or c in "._-")
        return f"{timestamp}_{safe_session_id}.md"

    async def start_new_session(self, session_id: str, database_name: str = "") -> None:
        """Start a new conversation session."""
        self.session_id = session_id
        filename = self._get_session_filename(session_id)
        self.current_session_file = self.history_dir / filename

        # Create initial markdown content
        initial_content = f"""# sq3m Conversation Session

**Session ID:** {session_id}
**Started:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Database:** {database_name if database_name else "Not specified"}

---

"""

        async with aiofiles.open(self.current_session_file, "w", encoding="utf-8") as f:
            await f.write(initial_content)

    async def add_user_query(self, query: str) -> None:
        """Add user query to the conversation history."""
        if not self.current_session_file:
            await self.start_new_session("default")

        content = f"""## User Query
**Time:** {datetime.now().strftime("%H:%M:%S")}

{query}

"""
        await self._append_to_file(content)

    async def add_sql_response(
        self,
        sql: str,
        explanation: str = "",
        confidence: float = 0.0,
        execution_result: str | None = None,
    ) -> None:
        """Add SQL response to the conversation history."""
        if not self.current_session_file:
            await self.start_new_session("default")

        content = f"""## Generated SQL
**Time:** {datetime.now().strftime("%H:%M:%S")}
**Confidence:** {confidence:.2%}

```sql
{sql}
```

**Explanation:** {explanation}

"""

        if execution_result:
            content += f"""**Execution Result:**
```
{execution_result}
```

"""

        await self._append_to_file(content)

    async def add_query_and_response(
        self,
        user_query: str,
        sql: str,
        explanation: str = "",
        confidence: float = 0.0,
        execution_result: str | None = None,
        retry_count: int = 0,
    ) -> None:
        """Add user query and SQL response together."""
        if not self.current_session_file:
            await self.start_new_session("default")

        timestamp = datetime.now().strftime("%H:%M:%S")

        content = f"""## Q&A Session
**Time:** {timestamp}

### User Question
{user_query}

### Generated SQL
**Confidence:** {confidence:.2%}
{f"**Retry Attempt:** {retry_count}" if retry_count > 0 else ""}

```sql
{sql}
```

**Explanation:** {explanation}

"""

        if execution_result:
            content += f"""### Execution Result
```
{execution_result}
```

"""

        content += "---\n\n"
        await self._append_to_file(content)

    async def add_analysis_result(
        self, schema_summary: str, tables_analyzed: int, analysis_time: float
    ) -> None:
        """Add schema analysis results to the history."""
        if not self.current_session_file:
            await self.start_new_session("default")

        content = f"""## Schema Analysis
**Time:** {datetime.now().strftime("%H:%M:%S")}
**Tables Analyzed:** {tables_analyzed}
**Analysis Time:** {analysis_time:.2f}s

{schema_summary}

---

"""
        await self._append_to_file(content)

    async def add_error(self, error_message: str, error_type: str = "Error") -> None:
        """Add error information to the history."""
        if not self.current_session_file:
            await self.start_new_session("default")

        content = f"""## {error_type}
**Time:** {datetime.now().strftime("%H:%M:%S")}

```
{error_message}
```

---

"""
        await self._append_to_file(content)

    async def add_custom_entry(self, title: str, content: str) -> None:
        """Add custom entry to the history."""
        if not self.current_session_file:
            await self.start_new_session("default")

        entry = f"""## {title}
**Time:** {datetime.now().strftime("%H:%M:%S")}

{content}

---

"""
        await self._append_to_file(entry)

    async def _append_to_file(self, content: str) -> None:
        """Append content to the current session file."""
        if not self.current_session_file:
            return

        async with aiofiles.open(self.current_session_file, "a", encoding="utf-8") as f:
            await f.write(content)

    async def get_session_content(self) -> str:
        """Get the content of the current session."""
        if not self.current_session_file or not self.current_session_file.exists():
            return ""

        async with aiofiles.open(self.current_session_file, encoding="utf-8") as f:
            content = await f.read()
            return str(content)

    async def close_session(self) -> Path | None:
        """Close the current session and return the file path."""
        if self.current_session_file:
            # Add session end marker
            end_content = f"""
---

**Session Ended:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
            await self._append_to_file(end_content)

            file_path = self.current_session_file
            self.current_session_file = None
            self.session_id = None
            return file_path

        return None

    def list_sessions(self) -> list[Path]:
        """List all conversation session files."""
        return sorted(
            self.history_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True
        )

    async def get_recent_sessions(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get information about recent sessions."""
        sessions = []
        session_files = self.list_sessions()[:limit]

        for session_file in session_files:
            try:
                async with aiofiles.open(session_file, encoding="utf-8") as f:
                    content = await f.read()

                # Extract basic info from the markdown content
                lines = content.split("\n")
                session_info = {
                    "filename": session_file.name,
                    "path": session_file,
                    "created": datetime.fromtimestamp(session_file.stat().st_ctime),
                    "modified": datetime.fromtimestamp(session_file.stat().st_mtime),
                    "size": session_file.stat().st_size,
                }

                # Try to extract session ID and database name
                for line in lines[:20]:  # Check first 20 lines
                    if "**Session ID:**" in line:
                        session_info["session_id"] = line.split("**Session ID:**")[
                            1
                        ].strip()
                    elif "**Database:**" in line:
                        session_info["database"] = line.split("**Database:**")[
                            1
                        ].strip()

                sessions.append(session_info)

            except Exception as e:
                # If there's an error reading the file, still include basic info
                sessions.append(
                    {
                        "filename": session_file.name,
                        "path": session_file,
                        "error": str(e),
                        "created": datetime.fromtimestamp(session_file.stat().st_ctime),
                        "modified": datetime.fromtimestamp(
                            session_file.stat().st_mtime
                        ),
                        "size": session_file.stat().st_size,
                    }
                )

        return sessions

    def get_current_session_info(self) -> dict[str, Any]:
        """Get information about the current session."""
        if not self.current_session_file:
            return {"active": False}

        return {
            "active": True,
            "session_id": self.session_id,
            "filename": self.current_session_file.name,
            "path": self.current_session_file,
            "created": datetime.fromtimestamp(self.current_session_file.stat().st_ctime)
            if self.current_session_file.exists()
            else None,
        }
