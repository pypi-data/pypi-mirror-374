# Contributing to SQ3M

Thank you for considering contributing to sq3m! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible using our [bug report template](.github/ISSUE_TEMPLATE/bug_report.md).

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please use our [feature request template](.github/ISSUE_TEMPLATE/feature_request.md).

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch** from `main`
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** following our coding standards
4. **Add tests** for new functionality
5. **Run the full test suite** to ensure nothing breaks
6. **Update documentation** if necessary
7. **Commit your changes** with descriptive commit messages
8. **Push to your fork** and create a pull request

## 🛠️ Development Setup

### Prerequisites

- **Python 3.10+**
- **uv** package manager (recommended)
- **Git**

### Initial Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/sq3m.git
cd sq3m

# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync --all-extras --dev

# Install pre-commit hooks
uv run pre-commit install
```

### Environment Configuration

Create a `.env` file for development:

```bash
# Required for testing
OPENAI_API_KEY=your_test_api_key

# Optional database configuration for integration tests
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_NAME=test_database
DB_USERNAME=test_user
DB_PASSWORD=test_password
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
uv run pytest

# Run only unit tests (fast)
uv run pytest tests/unit

# Run with coverage report
uv run pytest --cov=sq3m --cov-report=html

# Run specific test file
uv run pytest tests/unit/test_specific_module.py

# Run tests matching a pattern
uv run pytest -k "test_pattern"
```

### Test Categories

- **Unit Tests**: Fast, isolated tests in `tests/unit/`
- **Integration Tests**: Tests with external dependencies in `tests/integration/`
- **Slow Tests**: Long-running tests marked with `@pytest.mark.slow`

### Writing Tests

- Place unit tests in `tests/unit/` mirroring the source structure
- Use descriptive test names: `test_should_convert_natural_language_to_sql_when_given_valid_input`
- Follow AAA pattern: Arrange, Act, Assert
- Mock external dependencies in unit tests
- Use fixtures for common test data

Example test structure:
```python
def test_should_generate_sql_when_given_natural_language():
    # Arrange
    service = OpenAIService("test-key")
    tables = [create_test_table()]
    query = "Show all users"

    # Act
    result = service.generate_sql(query, tables)

    # Assert
    assert result.sql.strip().startswith("SELECT")
    assert "users" in result.sql.lower()
```

## 🎨 Code Style

### Code Formatting and Linting

We use **ruff** for both linting and formatting:

```bash
# Format code
uv run ruff format .

# Run linter
uv run ruff check .

# Fix auto-fixable issues
uv run ruff check --fix .
```

### Type Checking

We use **mypy** for static type checking:

```bash
# Run type checker
uv run mypy sq3m/
```

### Pre-commit Hooks

Pre-commit hooks run automatically on commit and include:
- Code formatting (ruff format)
- Linting (ruff check)
- Type checking (mypy)
- Import sorting
- Trailing whitespace removal

## 🏗️ Architecture Guidelines

sq3m follows **Clean Architecture** principles:

### Directory Structure

```
sq3m/
├── domain/           # Business logic (no external dependencies)
│   ├── entities/     # Core business objects
│   └── interfaces/   # Abstract interfaces
├── application/      # Use cases and business rules
│   ├── services/     # Application services
│   └── use_cases/    # Specific business use cases
├── infrastructure/   # External interfaces
│   ├── database/     # Database implementations
│   ├── llm/          # LLM service implementations
│   └── prompts/      # System prompts
├── interface/        # User interface
│   └── cli/          # CLI implementation
└── config/           # Configuration management
```

### Dependency Rules

1. **Domain layer** should not depend on anything
2. **Application layer** depends only on domain
3. **Infrastructure layer** implements domain interfaces
4. **Interface layer** coordinates between layers

### Coding Principles

- **Single Responsibility Principle**: Each class should have one reason to change
- **Dependency Inversion**: Depend on abstractions, not concretions
- **Interface Segregation**: Create focused, specific interfaces
- **Open/Closed Principle**: Open for extension, closed for modification

## 📝 Commit Message Guidelines

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **chore**: Changes to the build process or auxiliary tools

### Examples

```bash
feat: add support for PostgreSQL database connections
fix: handle connection timeout errors gracefully
docs: update installation instructions for macOS
test: add unit tests for SQL query validation
chore: update dependencies to latest versions
```

## 🌍 Internationalization

When adding new features that involve user-facing text:

1. **Add new language strings** to appropriate prompt files
2. **Update both English and Korean** versions
3. **Test language switching** functionality
4. **Consider cultural context** for non-English languages

## 🔒 Security Guidelines

- **Never commit secrets** or API keys
- **Use environment variables** for sensitive configuration
- **Sanitize user input** before processing
- **Follow secure coding practices** for database operations
- **Review dependencies** for known vulnerabilities

## 🚀 Release Process

Releases are automated through GitHub Actions:

1. **Create a new tag** following semantic versioning (e.g., `v1.2.3`)
2. **Push the tag** to trigger the release workflow
3. **GitHub Actions will**:
   - Run full test suite
   - Build the package
   - Publish to PyPI
   - Create GitHub release with changelog

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Code Review**: Submit PRs for feedback and guidance

## 📋 Checklist for Contributors

Before submitting a PR, ensure:

- [ ] Code follows the project style guidelines
- [ ] All tests pass locally
- [ ] New code has appropriate test coverage
- [ ] Documentation is updated if necessary
- [ ] Commit messages follow the convention
- [ ] PR description clearly explains the changes
- [ ] No sensitive information is committed

## 🙏 Recognition

All contributors will be recognized in our release notes and GitHub contributors section. Thank you for helping make sq3m better!

---

*This contributing guide is a living document. Please suggest improvements through issues or pull requests.*
