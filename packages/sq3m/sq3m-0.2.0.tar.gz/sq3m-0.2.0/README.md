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
```

## 🔧 How to Use

### Quick Start

1. **Install sq3m**:
   ```bash
   pip install sq3m
   ```

2. **Set up your OpenAI API key**:
   ```bash
   export OPENAI_API_KEY=your_openai_api_key
   ```

3. **Run the tool**:
   ```bash
   sq3m
   ```

### Step-by-Step Usage

When you run `sq3m`, the tool will guide you through an interactive setup:

#### 1. 🤖 **LLM Configuration**
- If `OPENAI_API_KEY` is not set, you'll be prompted to enter it
- Optionally configure the model (defaults to `gpt-3.5-turbo`)

#### 2. 🗄️ **Database Connection**
The tool will ask for your database details:
- **Database Type**: Choose between MySQL, PostgreSQL, or SQLite
- **Host**: Database server address (e.g., `localhost`)
- **Port**: Database port (e.g., `3306` for MySQL, `5432` for PostgreSQL)
- **Database Name**: Your database name
- **Username & Password**: Your database credentials

**Pro Tip**: Set these as environment variables to skip the interactive setup:
```bash
export DB_TYPE=mysql
export DB_HOST=localhost
export DB_PORT=3306
export DB_NAME=your_database
export DB_USERNAME=your_username
export DB_PASSWORD=your_password
```

#### 3. 📊 **Schema Analysis**
- sq3m automatically analyzes all tables in your database
- Uses AI to infer the purpose of each table
- Creates a comprehensive understanding of your database structure

#### 4. 💬 **Interactive Query Mode**
Now you can ask questions in natural language!

### 💡 Example Conversations

```
🤖 sq3m > Show me all users
Generated SQL:
SELECT * FROM users;

Results:
┌────┬──────────┬─────────────────────┬────────────────────┐
│ id │   name   │       email         │    created_at      │
├────┼──────────┼─────────────────────┼────────────────────┤
│ 1  │ John Doe │ john@example.com    │ 2024-01-15         │
│ 2  │ Jane Doe │ jane@example.com    │ 2024-01-16         │
└────┴──────────┴─────────────────────┴────────────────────┘

🤖 sq3m > How many orders were placed this month?
Generated SQL:
SELECT COUNT(*) as order_count
FROM orders
WHERE MONTH(created_at) = MONTH(CURRENT_DATE())
  AND YEAR(created_at) = YEAR(CURRENT_DATE());

Results:
┌─────────────┐
│ order_count │
├─────────────┤
│     47      │
└─────────────┘

🤖 sq3m > What are the top 3 selling products?
Generated SQL:
SELECT p.name, SUM(oi.quantity) as total_sold
FROM products p
JOIN order_items oi ON p.id = oi.product_id
GROUP BY p.id, p.name
ORDER BY total_sold DESC
LIMIT 3;

Results: [showing results...]
```

### 🎯 Available Commands

While in the interactive mode, you can use these special commands:

| Command | Description |
|---------|-------------|
| `tables` | Show all database tables and their AI-inferred purposes |
| `help` or `h` | Display available commands |
| `quit`, `exit`, or `q` | Exit the application |

### 🔧 Advanced Configuration

Create a `.env` file in your working directory:

```bash
# .env file
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4  # Use GPT-4 for better results

DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myapp_production
DB_USERNAME=myuser
DB_PASSWORD=mypassword
```

### 💡 Tips for Better Results

1. **Be Specific**: "Show users created this week" vs "Show users"
2. **Use Table Names**: If you know them, mention specific table names
3. **Ask Follow-ups**: "Can you also show their email addresses?"
4. **Use Business Terms**: "Show revenue by month" instead of "sum sales"

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
