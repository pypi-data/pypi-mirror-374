import os
import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

import pytest

from sq3m.infrastructure.prompts.prompt_loader import PromptLoader


@pytest.fixture  # type: ignore[misc]
def temp_dirs() -> Generator[dict[str, Any], None, None]:
    """Create temporary directories for testing."""
    temp_base = tempfile.mkdtemp()
    temp_paths = {
        "base": Path(temp_base),
        "config": Path(temp_base) / "config",
        "custom": Path(temp_base) / "custom",
    }

    for path in temp_paths.values():
        path.mkdir(exist_ok=True)

    yield temp_paths
    shutil.rmtree(temp_base)


@pytest.fixture  # type: ignore[misc]
def prompt_loader() -> Any:
    """Create PromptLoader instance."""
    return PromptLoader()


class TestPromptLoader:
    def test_init(self, prompt_loader: Any) -> None:
        """Test PromptLoader initialization."""
        assert prompt_loader.default_prompt_dir.exists()
        # Check that language-specific prompt files exist
        assert len(prompt_loader.language_prompts) == 2
        assert "en" in prompt_loader.language_prompts
        assert "ko" in prompt_loader.language_prompts
        assert prompt_loader.language_prompts["en"].exists()
        assert prompt_loader.language_prompts["ko"].exists()

    def test_load_default_system_prompt(self, prompt_loader: Any) -> None:
        """Test loading default system prompt."""
        prompt = prompt_loader.load_system_prompt()

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "database expert" in prompt.lower()

    def test_load_system_prompt_with_custom_path(
        self, prompt_loader: Any, temp_dirs: dict[str, Any]
    ) -> None:
        """Test loading system prompt from custom path."""
        custom_file = temp_dirs["custom"] / "custom_prompt.txt"
        custom_content = "Custom system prompt for testing"
        custom_file.write_text(custom_content)

        prompt = prompt_loader.load_system_prompt(str(custom_file))

        assert prompt == custom_content

    def test_load_system_prompt_with_env_path(
        self, prompt_loader: Any, temp_dirs: dict[str, Any]
    ) -> None:
        """Test loading system prompt from SYSTEM_PROMPT_PATH environment variable."""
        custom_file = temp_dirs["custom"] / "env_prompt.txt"
        custom_content = "Environment path prompt"
        custom_file.write_text(custom_content)

        with patch.dict(os.environ, {"SYSTEM_PROMPT_PATH": str(custom_file)}):
            prompt = prompt_loader.load_system_prompt()

        assert prompt == custom_content

    def test_load_system_prompt_with_env_file(
        self, prompt_loader: Any, temp_dirs: dict[str, Any]
    ) -> None:
        """Test loading system prompt from SYSTEM_PROMPT_FILE environment variable."""
        # Mock EnvironmentDetector to return our temp config dir
        mock_detector = Mock()
        mock_detector.config_dir = temp_dirs["config"]

        custom_file = temp_dirs["config"] / "env_file_prompt.txt"
        custom_content = "Environment file prompt"
        custom_file.write_text(custom_content)

        with (
            patch.dict(os.environ, {"SYSTEM_PROMPT_FILE": "env_file_prompt.txt"}),
            patch(
                "sq3m.infrastructure.config.env_detector.EnvironmentDetector",
                return_value=mock_detector,
            ),
        ):
            prompt = prompt_loader.load_system_prompt()

        assert prompt == custom_content

    def test_load_system_prompt_priority_order(
        self, prompt_loader: Any, temp_dirs: dict[str, Any]
    ) -> None:
        """Test that custom path parameter takes priority over environment variables."""
        # Create files for different sources
        custom_file = temp_dirs["custom"] / "custom.txt"
        env_path_file = temp_dirs["custom"] / "env_path.txt"
        env_file = temp_dirs["config"] / "env_file.txt"

        custom_file.write_text("custom path content")
        env_path_file.write_text("env path content")
        env_file.write_text("env file content")

        mock_detector = Mock()
        mock_detector.config_dir = temp_dirs["config"]

        with (
            patch.dict(
                os.environ,
                {
                    "SYSTEM_PROMPT_PATH": str(env_path_file),
                    "SYSTEM_PROMPT_FILE": "env_file.txt",
                },
            ),
            patch(
                "sq3m.infrastructure.config.env_detector.EnvironmentDetector",
                return_value=mock_detector,
            ),
        ):
            # Custom path should override environment variables
            prompt = prompt_loader.load_system_prompt(str(custom_file))
            assert prompt == "custom path content"

    def test_load_system_prompt_env_path_priority(
        self, prompt_loader: Any, temp_dirs: dict[str, Any]
    ) -> None:
        """Test that SYSTEM_PROMPT_PATH takes priority over SYSTEM_PROMPT_FILE."""
        env_path_file = temp_dirs["custom"] / "env_path.txt"
        env_file = temp_dirs["config"] / "env_file.txt"

        env_path_file.write_text("env path content")
        env_file.write_text("env file content")

        mock_detector = Mock()
        mock_detector.config_dir = temp_dirs["config"]

        with (
            patch.dict(
                os.environ,
                {
                    "SYSTEM_PROMPT_PATH": str(env_path_file),
                    "SYSTEM_PROMPT_FILE": "env_file.txt",
                },
            ),
            patch(
                "sq3m.infrastructure.config.env_detector.EnvironmentDetector",
                return_value=mock_detector,
            ),
        ):
            prompt = prompt_loader.load_system_prompt()
            assert prompt == "env path content"

    def test_load_system_prompt_file_not_found_fallback(
        self, prompt_loader: Any, temp_dirs: dict[str, Any]
    ) -> None:
        """Test fallback to default when custom file not found."""
        nonexistent_file = temp_dirs["custom"] / "nonexistent.txt"

        # Should fallback to default and not raise an error
        prompt = prompt_loader.load_system_prompt(str(nonexistent_file))

        # Should be default content
        assert "database expert" in prompt.lower()

    def test_load_system_prompt_no_files_error(
        self, prompt_loader: Any, temp_dirs: dict[str, Any]
    ) -> None:
        """Test error when no prompt files are available."""
        # Create a new prompt loader with non-existent files
        nonexistent_dir = temp_dirs["custom"] / "nonexistent"
        test_loader = PromptLoader()
        # Replace all file paths with non-existent ones
        test_loader.language_prompts = {
            "en": nonexistent_dir / "nonexistent_en.md",
            "ko": nonexistent_dir / "nonexistent_ko.md",
        }

        with pytest.raises(RuntimeError, match="System prompt file not found"):
            test_loader.load_system_prompt()

    def test_create_custom_prompt_template(
        self, prompt_loader: Any, temp_dirs: dict[str, Any]
    ) -> None:
        """Test creating custom prompt template."""
        template_path = temp_dirs["custom"] / "my_prompt.txt"

        created_path = prompt_loader.create_custom_prompt_template(str(template_path))

        assert created_path == template_path
        assert template_path.exists()

        content = template_path.read_text()
        assert "# Custom System Prompt for sq3m" in content
        assert "SYSTEM_PROMPT_PATH" in content
        assert "SYSTEM_PROMPT_FILE" in content
        # Should contain the default prompt as reference
        assert "database expert" in content.lower()

    def test_create_custom_prompt_template_creates_parent_dir(
        self, prompt_loader: Any, temp_dirs: dict[str, Any]
    ) -> None:
        """Test that template creation creates parent directories."""
        template_path = temp_dirs["custom"] / "subdir" / "nested" / "prompt.txt"

        created_path = prompt_loader.create_custom_prompt_template(str(template_path))

        assert created_path.exists()
        assert created_path.parent.exists()

    def test_get_available_prompts_default_only(self, prompt_loader: Any) -> None:
        """Test getting prompt info with language-specific prompts only."""
        info = prompt_loader.get_available_prompts()

        assert "current_prompt_path" in info
        assert info["current_prompt_exists"] is True
        assert "current_language" in info
        assert "available_languages" in info
        # Should not have env variables set when no env vars are provided
        assert info.get("env_prompt_path") is None
        assert info.get("env_file_path") is None
        # Should have language info
        assert info["current_language"] == "en"
        assert "en" in info["available_languages"]
        assert "ko" in info["available_languages"]

    def test_get_available_prompts_with_env_vars(
        self, prompt_loader: Any, temp_dirs: dict[str, Any]
    ) -> None:
        """Test getting prompt info with environment variables set."""
        env_path_file = temp_dirs["custom"] / "env_path.txt"
        env_file = temp_dirs["config"] / "env_file.txt"

        env_path_file.write_text("test")
        env_file.write_text("test")

        mock_detector = Mock()
        mock_detector.config_dir = temp_dirs["config"]

        with (
            patch.dict(
                os.environ,
                {
                    "SYSTEM_PROMPT_PATH": str(env_path_file),
                    "SYSTEM_PROMPT_FILE": "env_file.txt",
                },
            ),
            patch(
                "sq3m.infrastructure.config.env_detector.EnvironmentDetector",
                return_value=mock_detector,
            ),
        ):
            info = prompt_loader.get_available_prompts()

        assert info["env_prompt_path"] == str(env_path_file)
        assert info["env_prompt_exists"] is True
        assert info["env_file_path"] == str(temp_dirs["config"] / "env_file.txt")
        assert info["env_file_exists"] is True

    def test_resolve_prompt_path_precedence(
        self, prompt_loader: Any, temp_dirs: dict[str, Any]
    ) -> None:
        """Test _resolve_prompt_path follows correct precedence."""
        custom_file = temp_dirs["custom"] / "custom.txt"
        env_path_file = temp_dirs["custom"] / "env_path.txt"

        mock_detector = Mock()
        mock_detector.config_dir = temp_dirs["config"]

        with patch(
            "sq3m.infrastructure.config.env_detector.EnvironmentDetector",
            return_value=mock_detector,
        ):
            # Test custom path parameter (highest priority)
            path = prompt_loader._resolve_prompt_path(str(custom_file))
            assert path == custom_file

            # Test SYSTEM_PROMPT_PATH environment variable
            with patch.dict(os.environ, {"SYSTEM_PROMPT_PATH": str(env_path_file)}):
                path = prompt_loader._resolve_prompt_path()
                assert path == env_path_file

            # Test SYSTEM_PROMPT_FILE environment variable
            with patch.dict(os.environ, {"SYSTEM_PROMPT_FILE": "config_file.txt"}):
                path = prompt_loader._resolve_prompt_path()
                assert path == temp_dirs["config"] / "config_file.txt"

            # Test default fallback - should return language-specific (English default)
            # Since we're not setting LANGUAGE env var, it should return English
            path = prompt_loader._resolve_prompt_path()
            assert path == prompt_loader.language_prompts["en"]
