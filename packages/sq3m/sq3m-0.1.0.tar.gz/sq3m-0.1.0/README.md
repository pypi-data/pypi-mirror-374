# SQ3M - AI-Powered Database Query Assistant

<!-- Language Toggle -->
<div align="center">

[**🇺🇸 English**](#) | [**🇰🇷 한국어**](README_KR.md)

</div>

A Python CLI tool that converts natural language queries into SQL using Large Language Models (LLM). Built with Clean Architecture principles.

## 🚀 Features

- 🤖 **Natural language to SQL conversion** using OpenAI completion models
- 🗄️ **Multi-database support** for MySQL and PostgreSQL
- 🧠 **Automatic table purpose inference** using LLM
- 🎨 **Beautiful CLI interface** with Rich
- ⚙️ **Environment variable configuration**
- 🏗️ **Clean Architecture design**

## 📦 Installation

### Using pip
```bash
pip install sq3m
```

### Using uv (recommended for development)
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository and setup
git clone https://github.com/leegyurak/sq3m.git
cd sq3m
uv sync
```

## ⚙️ Configuration

Set up your environment variables in a `.env` file or export them:

```bash
# OpenAI Configuration
export OPENAI_API_KEY=your_openai_api_key
export OPENAI_MODEL=gpt-3.5-turbo  # Optional, defaults to gpt-3.5-turbo

# Database Configuration (Optional - can be set interactively)
export DB_TYPE=mysql  # mysql or postgresql
export DB_HOST=localhost
export DB_PORT=3306
export DB_NAME=your_database
export DB_USERNAME=your_username
export DB_PASSWORD=your_password

# Language Configuration (Optional)
export LANGUAGE=en  # en (English) or ko (Korean), defaults to en
```

### 🌍 Multi-language Support

sq3m supports multiple system prompt languages through the `LANGUAGE` environment variable:

- **Supported Languages**:
  - `en`: English (default)
  - `ko`: Korean

- **Priority Order for System Prompts**:
  1. Custom path parameter (directly specified)
  2. `SYSTEM_PROMPT_PATH` environment variable (absolute path)
  3. `SYSTEM_PROMPT_FILE` environment variable (filename in config directory)
  4. **Language-specific default prompt** (based on LANGUAGE environment variable)
  5. Default fallback prompt

**Example Usage:**
```bash
# Use Korean system prompts
export LANGUAGE=ko
sq3m

# Or set in .env file
echo "LANGUAGE=ko" >> .env
```

## 🔧 Usage

Run the CLI tool:

```bash
sq3m
```

The tool will guide you through:

1. **🤖 LLM Setup**: Configure OpenAI API key (if not in environment)
2. **🗄️ Database Connection**: Set up database connection (interactive if not in environment)
3. **📊 Schema Analysis**: Automatically analyze all tables and infer their purposes
4. **💬 Interactive Queries**: Ask questions in natural language

### 💡 Example Queries

- "Show all users"
- "Find orders from last month"
- "Count products by category"
- "Show user details for user ID 123"
- "What are the top 5 selling products?"

### 🎯 CLI Commands

- `tables` - Show all database tables and their purposes
- `help` or `h` - Show available commands
- `quit`, `exit`, or `q` - Exit the application

## 🏗️ Architecture

The project follows Clean Architecture principles:

```
sq3m/
├── domain/           # Business logic and entities
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

## 🛠️ Development

### Prerequisites

- **Python 3.10+**
- **uv** package manager (recommended for fast dependency management)

### UV Package Manager Setup

This project uses [uv](https://github.com/astral-sh/uv) for fast Python package management.

**Install uv:**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv
```

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/leegyurak/sq3m.git
cd sq3m

# Initialize Python environment and install dependencies
uv sync --all-extras --dev

# Install pre-commit hooks
uv run pre-commit install
```

**Activate Virtual Environment (optional):**
```bash
# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### Development Workflow

1. **Make changes** to the code
2. **Run tests**: `uv run pytest`
3. **Run linting**: `uv run ruff check --fix .`
4. **Run formatting**: `uv run ruff format .`
5. **Run type checking**: `uv run mypy sq3m/`
6. **Commit changes** (pre-commit hooks will run automatically)

### Running Tests

```bash
# Run all tests
uv run pytest

# Run unit tests only
uv run pytest tests/unit

# Run integration tests
uv run pytest tests/integration

# Run with coverage
uv run pytest --cov=sq3m

# Run tests excluding slow ones
uv run pytest -m "not slow"
```

### Code Quality

```bash
# Linting and formatting with ruff
uv run ruff check --fix .
uv run ruff format .

# Type checking
uv run mypy sq3m/

# Pre-commit hooks (run automatically on commit)
uv run pre-commit run --all-files
```

### Running the Application

```bash
# Run directly with uv
uv run sq3m

# Or activate environment first
source .venv/bin/activate
sq3m
```

## 📚 Dependencies

### Runtime Dependencies
- **click**: CLI framework
- **rich**: Beautiful terminal UI
- **openai**: OpenAI API client
- **python-dotenv**: Environment variable management
- **psycopg2-binary**: PostgreSQL driver
- **pymysql**: MySQL driver
- **sqlparse**: SQL parsing utilities
- **pydantic**: Data validation

### Development Dependencies
- **pytest**: Testing framework
- **pytest-cov**: Coverage reporting
- **pytest-asyncio**: Async testing support
- **ruff**: Fast Python linter and formatter
- **pre-commit**: Git hooks framework
- **mypy**: Static type checker

## 📋 Requirements

- **Python**: 3.10 or higher
- **uv**: Package manager (recommended) or pip

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Thanks to OpenAI for providing the completion models
- Built with modern Python tools: uv, ruff, pytest
- Inspired by Clean Architecture principles
