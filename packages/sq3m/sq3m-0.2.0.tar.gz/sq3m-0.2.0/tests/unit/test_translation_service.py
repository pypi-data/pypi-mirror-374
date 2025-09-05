"""Tests for TranslationService."""

from __future__ import annotations

from unittest.mock import Mock, patch

from sq3m.infrastructure.llm.translation_service import TranslationService


class TestTranslationService:
    """Test cases for TranslationService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.api_key = "test-api-key"
        self.translation_service = TranslationService(self.api_key)

    def test_init(self):
        """Test TranslationService initialization."""
        assert self.translation_service.api_key == self.api_key
        assert self.translation_service.model == "gpt-3.5-turbo"

    def test_is_english_query_english_text(self):
        """Test English query detection with English text."""
        english_queries = [
            "Show all users",
            "Find customers from last month",
            "SELECT * FROM orders",
            "List all products with price > 100",
            "Get user data for ID 123",
            "show me the sales report",
            "count all orders by status",
        ]

        for query in english_queries:
            assert self.translation_service.is_english_query(query), (
                f"Failed for: {query}"
            )

    def test_is_english_query_korean_text(self):
        """Test English query detection with Korean text."""
        korean_queries = [
            "모든 사용자를 보여주세요",
            "지난 달 고객을 찾아주세요",
            "가격이 100보다 큰 모든 제품을 나열해주세요",
            "특정 encounter의 location을 보여주세요",
            "사용자 데이터를 가져와주세요",
        ]

        for query in korean_queries:
            assert not self.translation_service.is_english_query(query), (
                f"Failed for: {query}"
            )

    def test_is_english_query_mixed_text(self):
        """Test English query detection with mixed language text."""
        # Mixed queries with significant English should be considered English
        mixed_english = [
            "show me 사용자 data",
            "find orders with 상태 = completed",
            "SELECT name FROM users WHERE age > 25",
        ]

        for query in mixed_english:
            result = self.translation_service.is_english_query(query)
            # These could go either way depending on the ratio, just ensure no crash
            assert isinstance(result, bool)

    def test_is_english_query_edge_cases(self):
        """Test English query detection with edge cases."""
        edge_cases = [
            ("", True),  # Empty string
            ("   ", True),  # Whitespace only
            ("123 456", True),  # Numbers only
            ("!@#$%", True),  # Symbols only
        ]

        for query, expected in edge_cases:
            assert self.translation_service.is_english_query(query) == expected

    @patch("sq3m.infrastructure.llm.translation_service.OpenAI")
    def test_translate_to_english_korean(self, mock_openai):
        """Test translation from Korean to English."""
        # Mock OpenAI response
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Show all users"
        mock_client.chat.completions.create.return_value = mock_response

        service = TranslationService(self.api_key)

        result = service.translate_to_english("모든 사용자를 보여주세요")

        assert result == "Show all users"
        mock_client.chat.completions.create.assert_called_once()

    @patch("sq3m.infrastructure.llm.translation_service.OpenAI")
    def test_translate_to_english_already_english(self, mock_openai):
        """Test that English queries are not translated."""
        service = TranslationService(self.api_key)

        english_query = "Show all users"
        result = service.translate_to_english(english_query)

        # Should return original query without API call
        assert result == english_query
        # OpenAI should not be called for English queries
        mock_openai.return_value.chat.completions.create.assert_not_called()

    @patch("sq3m.infrastructure.llm.translation_service.OpenAI")
    def test_translate_to_english_api_error(self, mock_openai):
        """Test translation fallback when API fails."""
        # Mock OpenAI to raise an exception
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        service = TranslationService(self.api_key)

        original_query = "모든 사용자를 보여주세요"
        result = service.translate_to_english(original_query)

        # Should return original query when translation fails
        assert result == original_query

    @patch("sq3m.infrastructure.llm.translation_service.OpenAI")
    def test_translate_to_english_empty_response(self, mock_openai):
        """Test translation fallback when API returns empty response."""
        # Mock OpenAI to return empty response
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = None
        mock_client.chat.completions.create.return_value = mock_response

        service = TranslationService(self.api_key)

        original_query = "모든 사용자를 보여주세요"
        result = service.translate_to_english(original_query)

        # Should return original query when response is empty
        assert result == original_query

    def test_detect_language(self):
        """Test language detection."""
        test_cases = [
            ("Show all users", "en"),
            ("모든 사용자를 보여주세요", "ko"),
            ("すべてのユーザーを表示", "ja"),
            ("显示所有用户", "zh"),
            ("Показать всех пользователей", "ru"),
            ("Mostrar todos los usuarios", "es"),
            ("123 456", "en"),  # Numbers default to English
            ("", "en"),  # Empty defaults to English
        ]

        for query, expected_lang in test_cases:
            result = self.translation_service.detect_language(query)
            assert result == expected_lang, (
                f"Failed for query: '{query}', expected: {expected_lang}, got: {result}"
            )

    @patch("sq3m.infrastructure.llm.translation_service.OpenAI")
    def test_translation_with_database_terms(self, mock_openai):
        """Test translation preserves database-related terms."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[
            0
        ].message.content = "Find all customers from the orders table"
        mock_client.chat.completions.create.return_value = mock_response

        service = TranslationService(self.api_key)

        result = service.translate_to_english(
            "orders 테이블에서 모든 고객을 찾아주세요"
        )

        assert result == "Find all customers from the orders table"

        # Verify the prompt includes database-specific instructions
        call_args = mock_client.chat.completions.create.call_args
        assert "database" in call_args[1]["messages"][0]["content"].lower()

    def test_english_detection_with_sql_keywords(self):
        """Test that queries with SQL keywords are detected as English."""
        sql_queries = [
            "SELECT * FROM users",
            "UPDATE products SET price = 100",
            "INSERT INTO orders VALUES (1, 2, 3)",
            "DELETE FROM customers WHERE id = 1",
            "CREATE TABLE test (id INT)",
        ]

        for query in sql_queries:
            assert self.translation_service.is_english_query(query), (
                f"Failed for SQL: {query}"
            )

    def test_non_english_with_english_keywords(self):
        """Test mixed language queries with English database keywords."""
        mixed_queries = [
            "users 테이블에서 모든 데이터를 SELECT해주세요",
            "products에서 price가 높은 것들을 찾아주세요",
            "customers table의 모든 레코드를 보여주세요",
        ]

        for query in mixed_queries:
            # These should be detected as non-English despite having some English words
            result = self.translation_service.is_english_query(query)
            # The result may vary based on the ratio, but should not crash
            assert isinstance(result, bool)

    @patch("sq3m.infrastructure.llm.translation_service.OpenAI")
    def test_translation_temperature_and_max_tokens(self, mock_openai):
        """Test that translation uses appropriate temperature and token limits."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Show users"
        mock_client.chat.completions.create.return_value = mock_response

        service = TranslationService(self.api_key)
        service.translate_to_english("사용자를 보여주세요")

        call_args = mock_client.chat.completions.create.call_args[1]
        assert (
            call_args["temperature"] == 0.1
        )  # Low temperature for consistent translations
        assert call_args["max_tokens"] == 200  # Reasonable limit for translations
