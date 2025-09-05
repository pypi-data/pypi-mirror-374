from __future__ import annotations

import os
from pathlib import Path


class PromptLoader:
    """Loads system prompts from files with environment variable support."""

    def __init__(self) -> None:
        self.default_prompt_dir = Path(__file__).parent
        self.default_prompt_file = (
            self.default_prompt_dir / "default_system_prompt_en.md"
        )

    def load_system_prompt(self, custom_path: str | None = None) -> str:
        """
        Load system prompt from file.

        Priority order:
        1. custom_path parameter (if provided)
        2. SYSTEM_PROMPT_PATH environment variable
        3. SYSTEM_PROMPT_FILE environment variable (filename in config dir)
        4. Default system prompt file

        Args:
            custom_path: Optional direct path to prompt file

        Returns:
            System prompt content as string
        """
        prompt_path = self._resolve_prompt_path(custom_path)

        try:
            return prompt_path.read_text(encoding="utf-8").strip()
        except FileNotFoundError:
            # If custom path fails, try to fallback to default prompt
            if (
                custom_path
                or os.getenv("SYSTEM_PROMPT_PATH")
                or os.getenv("SYSTEM_PROMPT_FILE")
            ):
                print(f"Warning: Custom system prompt file not found at {prompt_path}")
                print("Falling back to default system prompt")
                if self.default_prompt_file.exists():
                    return self.default_prompt_file.read_text(encoding="utf-8").strip()

            raise RuntimeError(
                f"System prompt file not found at {prompt_path} and default prompt not available"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load system prompt from {prompt_path}: {e}")

    def _resolve_prompt_path(self, custom_path: str | None = None) -> Path:
        """Resolve the path to the system prompt file based on priority."""

        # 1. Direct custom path parameter
        if custom_path:
            return Path(custom_path)

        # 2. SYSTEM_PROMPT_PATH environment variable (absolute path)
        env_path = os.getenv("SYSTEM_PROMPT_PATH")
        if env_path:
            return Path(env_path)

        # 3. SYSTEM_PROMPT_FILE environment variable (filename in config dir)
        env_file = os.getenv("SYSTEM_PROMPT_FILE")
        if env_file:
            # Get config directory from environment detector
            from sq3m.infrastructure.config.env_detector import EnvironmentDetector

            detector = EnvironmentDetector()
            config_dir = detector.config_dir
            return config_dir / env_file

        # 4. Default system prompt file
        return self.default_prompt_file

    def create_custom_prompt_template(self, output_path: str) -> Path:
        """
        Create a custom system prompt template file.

        Args:
            output_path: Path where to create the template

        Returns:
            Path to the created template file
        """
        output_file = Path(output_path)

        # Ensure parent directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Load default prompt as template
        default_content = self.load_system_prompt()

        template_content = f"""# Custom System Prompt for sq3m
#
# This is a template based on the default system prompt.
# Modify this file to customize the AI's behavior and instructions.
#
# Environment variable options:
# - Set SYSTEM_PROMPT_PATH=/path/to/this/file to use this prompt
# - Set SYSTEM_PROMPT_FILE=filename.txt to use a file in the config directory
#
# Original default prompt:

{default_content}

#
# Add your customizations below:
#

"""

        output_file.write_text(template_content, encoding="utf-8")
        return output_file

    def get_available_prompts(self) -> dict[str, str | bool | list[str]]:
        """Get information about available prompt sources."""
        info: dict[str, str | bool | list[str]] = {}

        # Check environment variables
        env_path = os.getenv("SYSTEM_PROMPT_PATH")
        if env_path:
            info["env_prompt_path"] = env_path
            info["env_prompt_exists"] = Path(env_path).exists()

        env_file = os.getenv("SYSTEM_PROMPT_FILE")
        if env_file:
            from sq3m.infrastructure.config.env_detector import EnvironmentDetector

            detector = EnvironmentDetector()
            config_path = detector.config_dir / env_file
            info["env_file_path"] = str(config_path)
            info["env_file_exists"] = config_path.exists()

        # Get currently resolved path
        current_path = self._resolve_prompt_path()
        info["current_prompt_path"] = str(current_path)
        info["current_prompt_exists"] = current_path.exists()

        return info
