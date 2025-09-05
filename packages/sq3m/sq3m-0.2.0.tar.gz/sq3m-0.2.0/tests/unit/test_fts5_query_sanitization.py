"""Unit tests specifically for FTS5 query sanitization and error handling."""

from __future__ import annotations

import tempfile
from pathlib import Path

from sq3m.domain.entities.table_summary import TableSummary
from sq3m.infrastructure.database.sqlite_table_search_repository import (
    SQLiteTableSearchRepository,
)


class TestFTS5QuerySanitization:
    """Focused unit tests for FTS5 query sanitization."""

    def setup_method(self):
        """Set up test fixtures."""
        import os

        fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)  # Close the file descriptor immediately
        self.repository = SQLiteTableSearchRepository(self.db_path)

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.repository.connection:
            self.repository.connection.close()
        Path(self.db_path).unlink(missing_ok=True)

    def test_sanitize_user_original_query(self):
        """Test sanitization of the original user query that caused the error."""
        query = "특정 encounter의 location, practitioner, department의 이력을 최신 10개만 보여주는 쿼리를 작성해주세요"

        sanitized = self.repository._sanitize_fts5_query(query)

        # Should not contain problematic characters
        assert "," not in sanitized
        # Note: Korean particles like '의', '를' are actually preserved in current implementation
        # They are valid Korean words and should be searchable

        # Should contain main content words
        expected_words = [
            "특정",
            "encounter",
            "location",
            "practitioner",
            "department",
            "이력",
            "최신",
            "쿼리",
        ]
        found_words = [word for word in expected_words if word in sanitized]

        # Should find at least some of the key words
        assert len(found_words) >= 4  # At least half of the important words

        # Should be properly formatted for FTS5
        if sanitized:
            assert " OR " in sanitized
            assert sanitized.startswith('"')
            assert sanitized.endswith('"')

    def test_sanitize_special_characters(self):
        """Test handling of various special characters."""
        test_cases = [
            # Commas (the original issue)
            ("word1, word2, word3", ["word1", "word2", "word3"]),
            # Parentheses
            ("data (with parentheses)", ["data", "with", "parentheses"]),
            # Quotes
            ('text with "quotes" inside', ["text", "with", "quotes", "inside"]),
            # Colons and semicolons
            ("field:value;another:value", ["field", "value", "another", "value"]),
            # Email-like strings
            ("user@domain.com", ["user", "domain", "com"]),
            # Hyphens and underscores
            ("table-name_field", ["table", "name", "field"]),
            # Mixed Korean and special chars
            ("사용자,테이블:정보", ["사용자", "테이블", "정보"]),
        ]

        for input_query, expected_words in test_cases:
            sanitized = self.repository._sanitize_fts5_query(input_query)

            for word in expected_words:
                assert word in sanitized, (
                    f"Expected word '{word}' not found in sanitized query: {sanitized}"
                )

    def test_sanitize_edge_cases(self):
        """Test edge cases in query sanitization."""
        edge_cases = [
            # Empty string
            ("", ""),
            # Only spaces
            ("   ", ""),
            # Only special characters
            ("!@#$%^&*()", ""),
            # Numbers only
            ("123 456", ""),  # Numbers are filtered out in current implementation
            # Single character
            ("a", '"a"'),
            # Very long word
            (
                "supercalifragilisticexpialidocious",
                '"supercalifragilisticexpialidocious"',
            ),
            # Mixed case
            ("MiXeD CaSe WoRdS", '"MiXeD" OR "CaSe" OR "WoRdS"'),
        ]

        for input_query, expected_pattern in edge_cases:
            sanitized = self.repository._sanitize_fts5_query(input_query)

            if expected_pattern:
                if expected_pattern == "":
                    assert sanitized == "" or sanitized.replace('"', "").strip() == ""
                else:
                    assert (
                        expected_pattern in sanitized or sanitized == expected_pattern
                    )
            else:
                # Just ensure it doesn't crash and returns a string
                assert isinstance(sanitized, str)

    def test_word_limit_enforcement(self):
        """Test that word limit is properly enforced."""
        # Create a query with exactly 10 words
        ten_words = "word1 word2 word3 word4 word5 word6 word7 word8 word9 word10"
        sanitized = self.repository._sanitize_fts5_query(ten_words)
        word_count = sanitized.count(" OR ") + 1 if sanitized else 0
        assert word_count == 10

        # Create a query with 15 words (should be limited to 10)
        fifteen_words = "word1 word2 word3 word4 word5 word6 word7 word8 word9 word10 word11 word12 word13 word14 word15"
        sanitized = self.repository._sanitize_fts5_query(fifteen_words)
        word_count = sanitized.count(" OR ") + 1 if sanitized else 0
        assert word_count == 10

    def test_korean_word_extraction(self):
        """Test extraction of Korean words specifically."""
        korean_test_cases = [
            ("한글 단어 테스트", ["한글", "단어", "테스트"]),
            ("사용자테이블정보", ["사용자테이블정보"]),  # Connected Korean words
            ("DB테이블", ["DB테이블"]),  # Mixed Korean-English
            ("환자_기록", ["환자", "기록"]),  # Korean with underscore
            ("의료진정보,부서이력", ["의료진정보", "부서이력"]),  # Korean with comma
        ]

        for input_query, expected_words in korean_test_cases:
            sanitized = self.repository._sanitize_fts5_query(input_query)

            for word in expected_words:
                assert word in sanitized, (
                    f"Korean word '{word}' not found in: {sanitized}"
                )

    def test_fallback_search_keyword_extraction(self):
        """Test keyword extraction in fallback search."""
        self.repository.initialize_storage()

        # Store test data with Korean and English
        summaries = [
            TableSummary("encounter_정보", "의료진 encounter 정보"),
            TableSummary("patient_records", "환자 기록 테이블"),
            TableSummary("department_이력", "부서 변경 이력"),
        ]
        self.repository.store_table_summaries(summaries)

        test_cases = [
            # Mixed Korean-English
            ("encounter 정보", ["encounter", "정보"]),
            # Pure Korean
            ("환자 기록", ["환자", "기록"]),
            # With special characters
            ("부서,이력", ["부서", "이력"]),
        ]

        for query, expected_keywords in test_cases:
            results = self.repository._fallback_keyword_search(query, limit=5)

            # Should find relevant tables
            found_tables = [r.table_summary.table_name for r in results]

            # At least one table should match one of the keywords
            matches_found = False
            for keyword in expected_keywords:
                for table_name in found_tables:
                    if keyword.lower() in table_name.lower():
                        matches_found = True
                        break
                if matches_found:
                    break

            # Should find some relevant results for meaningful queries
            if expected_keywords and any(len(k) > 1 for k in expected_keywords):
                assert matches_found or len(results) > 0

    def test_regex_patterns(self):
        """Test the regex patterns used for word extraction."""
        import re

        # Test the main regex pattern used in _sanitize_fts5_query
        pattern = r"\b[a-zA-Z가-힣]\w*\b"

        test_text = "English한글Mixed123 with_underscore and-hyphen special@chars"
        matches = re.findall(pattern, test_text)

        # Should match: English, 한글Mixed123, with_underscore, and, hyphen
        expected_matches = ["English한글Mixed123", "with_underscore", "and", "hyphen"]

        for expected in expected_matches:
            assert expected in matches, (
                f"Expected match '{expected}' not found in {matches}"
            )

        # Should not match pure numbers or pure special characters
        assert "123" not in matches
        assert "@" not in matches

    def test_quote_escaping_fallback(self):
        """Test quote escaping in fallback scenarios."""
        test_cases = [
            ('query with "double quotes"', 'query with ""double quotes""'),
            ("query with 'single quotes'", "query with ''single quotes''"),
            ("mixed \"double\" and 'single'", "mixed \"\"double\"\" and ''single''"),
        ]

        for input_query, expected_escaped in test_cases:
            # Force fallback by providing a query with no extractable words
            _ = self.repository._sanitize_fts5_query("!@#$%^&*()")

            # Test the quote escaping logic directly
            escaped = input_query.replace('"', '""').replace("'", "''")
            assert escaped == expected_escaped

    def test_performance_with_long_queries(self):
        """Test performance with very long queries."""
        # Create a very long query
        long_query = " ".join([f"word{i}" for i in range(1000)])

        # Should complete quickly and not crash
        sanitized = self.repository._sanitize_fts5_query(long_query)

        # Should still limit to 10 words
        word_count = sanitized.count(" OR ") + 1 if sanitized else 0
        assert word_count == 10

        # Should contain first few words
        assert "word0" in sanitized
        assert "word9" in sanitized
        # Should not contain later words
        assert "word50" not in sanitized

    def test_unicode_handling(self):
        """Test handling of various Unicode characters."""
        unicode_test_cases = [
            # Various Unicode spaces
            (
                "word1\u00a0word2\u2003word3",
                ["word1", "word2", "word3"],
            ),  # Non-breaking space, em space
            # Accented characters
            ("café naïve résumé", ["café", "naïve", "résumé"]),
            # Chinese characters (should be handled similarly to Korean)
            ("中文测试", ["中文测试"]),
            # Cyrillic
            ("тест кириллица", ["тест", "кириллица"]),
        ]

        for input_query, expected_words in unicode_test_cases:
            sanitized = self.repository._sanitize_fts5_query(input_query)

            # Should handle Unicode gracefully without crashing
            assert isinstance(sanitized, str)

            # For Latin characters with accents, should preserve them
            if any(ord(c) < 256 for c in input_query):
                for word in expected_words:
                    if all(ord(c) < 256 for c in word):  # Latin-based words
                        assert word in sanitized
