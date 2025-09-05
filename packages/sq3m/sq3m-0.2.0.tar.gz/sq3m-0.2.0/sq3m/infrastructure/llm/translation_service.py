"""Translation service for converting non-English queries to English."""

from __future__ import annotations

import re

from openai import OpenAI


class TranslationService:
    """Service for detecting language and translating queries to English."""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def is_english_query(self, query: str) -> bool:
        """
        Detect if a query is primarily in English.
        Uses simple heuristics to avoid unnecessary API calls.
        """
        if not query or not query.strip():
            return True

        # Remove common SQL keywords and punctuation for analysis
        clean_query = re.sub(r"[^\w\s]", " ", query.lower())
        words = clean_query.split()

        if len(words) == 0:
            return True

        # Common English words in database queries
        english_indicators = {
            "show",
            "find",
            "get",
            "list",
            "display",
            "select",
            "from",
            "where",
            "table",
            "tables",
            "data",
            "records",
            "users",
            "user",
            "customers",
            "customer",
            "orders",
            "order",
            "products",
            "product",
            "sales",
            "sale",
            "count",
            "sum",
            "total",
            "average",
            "max",
            "min",
            "group",
            "by",
            "having",
            "join",
            "inner",
            "left",
            "right",
            "outer",
            "on",
            "as",
            "and",
            "or",
            "not",
            "like",
            "in",
            "between",
            "is",
            "null",
            "asc",
            "desc",
            "limit",
            "offset",
            "distinct",
            "all",
            "any",
            "exists",
            "create",
            "update",
            "delete",
            "insert",
            "into",
            "values",
            "set",
            "alter",
            "drop",
            "index",
            "view",
            "database",
            "schema",
            "primary",
            "foreign",
            "key",
            "references",
            "constraint",
            "unique",
            "check",
            "default",
            "auto_increment",
            "varchar",
            "int",
            "integer",
            "decimal",
            "date",
            "datetime",
            "timestamp",
            "text",
            "boolean",
            "char",
            "time",
        }

        # Check for non-ASCII characters (likely non-English)
        has_non_ascii = any(ord(char) > 127 for char in query)

        # Count English indicator words
        english_word_count = sum(1 for word in words if word in english_indicators)
        english_ratio = english_word_count / len(words) if words else 0

        # Heuristic: Consider it English if:
        # 1. No non-ASCII characters and some English indicators (>10%), OR
        # 2. High ratio of English indicators (>= 30%)
        if not has_non_ascii and english_ratio > 0.1 or english_ratio >= 0.3:
            return True
        elif has_non_ascii and english_ratio < 0.2:
            return False
        elif not has_non_ascii and english_ratio == 0:
            # No English indicators and no non-ASCII - check for common non-English patterns
            spanish_patterns = [
                "mostrar",
                "todos",
                "usuarios",
                "ver",
                "buscar",
                "los",
                "las",
                "el",
                "la",
            ]
            if any(word in query.lower() for word in spanish_patterns):
                return False

        # For borderline cases with some English indicators, assume English
        return not has_non_ascii

    def translate_to_english(self, query: str) -> str:
        """
        Translate a non-English query to English using OpenAI.

        Args:
            query: The input query in any language

        Returns:
            English translation of the query
        """
        if self.is_english_query(query):
            return query

        try:
            prompt = f"""Translate the following database query from any language to clear, natural English.
The query is asking about database operations, so preserve the meaning and intent for SQL generation.

Original query: {query}

Translate to English (respond with only the translation):"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful translator. Translate database queries to clear English while preserving the database operation intent.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,  # Low temperature for consistent translations
                max_tokens=200,
            )

            translation = response.choices[0].message.content
            if translation:
                translated = translation.strip()
                # Basic validation that we got a reasonable translation
                if len(translated) > 0 and len(translated) < len(query) * 3:
                    print(f"🌐 Translated query: '{query}' → '{translated}'")
                    return translated

            # Fallback to original if translation failed
            print(f"⚠️ Translation failed, using original query: {query}")
            return query

        except Exception as e:
            print(f"⚠️ Translation error: {e}, using original query")
            return query

    def detect_language(self, query: str) -> str:
        """
        Detect the language of a query (for informational purposes).

        Args:
            query: The input query

        Returns:
            Detected language code (e.g., 'ko', 'ja', 'zh', 'es', 'en', etc.)
        """
        if self.is_english_query(query):
            return "en"

        # Simple character-based language detection
        if re.search(r"[가-힣]", query):
            return "ko"  # Korean
        elif re.search(r"[ひらがなカタカナァ-ヶ]", query):
            return "ja"  # Japanese (hiragana/katakana)
        elif re.search(r"[一-龯]", query):
            # Check for Japanese-specific kanji combinations
            japanese_patterns = ["すべて", "ユーザー", "表示", "を", "の"]
            if any(pattern in query for pattern in japanese_patterns):
                return "ja"
            return "zh"  # Chinese
        elif re.search(r"[а-яё]", query, re.IGNORECASE):
            return "ru"  # Russian
        elif re.search(r"[àáâãäåçèéêëìíîïñòóôõöùúûüý]", query, re.IGNORECASE):
            # Could be Spanish, French, Portuguese, etc.
            return "es"  # Assume Spanish as common case
        elif any(
            word in query.lower()
            for word in ["mostrar", "todos", "usuarios", "ver", "buscar"]
        ):
            return "es"  # Spanish indicators
        else:
            return "unknown"
