# Bank Statement Separator

[![Documentation](https://img.shields.io/badge/docs-online-blue)](https://madeinoz67.github.io/bank-statement-separator/)
[![Tests](https://img.shields.io/badge/tests-37%2F37%20passing-brightgreen)](https://github.com/madeinoz67/bank-statement-separator/actions)

An AI-powered tool that automatically processes PDF files containing multiple bank statements and separates them into individual files. Built with LangChain and LangGraph for robust stateful AI processing.

## 🚀 Features

- **AI-Powered Analysis**: Uses advanced language models to detect statement boundaries
- **Multiple LLM Support**: Compatible with OpenAI GPT models and Ollama local models
- **PDF Processing**: Efficient document manipulation using PyMuPDF
- **Metadata Extraction**: Automatically extracts account numbers, dates, and bank information
- **File Organization**: Generates meaningful filenames following configurable patterns
- **Error Handling**: Comprehensive logging and audit trails
- **Security Controls**: Built-in safeguards for production use
- **Paperless Integration**: Optional integration with Paperless-ngx for document management

## 📋 Requirements

- Python 3.9+
- OpenAI API key (for LLM functionality)
- UV package manager

## 🛠 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/madeinoz67/bank-statement-separator.git
cd bank-statement-separator
```

### 2. Install Dependencies

```bash
# Install with UV
uv sync

# Install with dev dependencies
uv sync --group dev
```

### 3. Configure Environment

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` to set your OpenAI API key:
```bash
OPENAI_API_KEY=your_api_key_here
```

## 📖 Usage

### Basic Usage

```bash
# Process a single PDF file
uv run python -m src.bank_statement_separator.main input.pdf

# Specify output directory
uv run python -m src.bank_statement_separator.main input.pdf -o ./output

# Use verbose logging
uv run python -m src.bank_statement_separator.main input.pdf --verbose

# Dry run mode (no files written)
uv run python -m src.bank_statement_separator.main input.pdf --dry-run
```

### Advanced Options

```bash
# Specify LLM model
uv run python -m src.bank_statement_separator.main input.pdf --model gpt-4o

# Set custom processing limits
uv run python -m src.bank_statement_separator.main input.pdf --max-pages 50

# Enable debug mode
uv run python -m src.bank_statement_separator.main input.pdf --debug
```

### Configuration

The application uses environment variables for configuration. Key settings include:

- `OPENAI_API_KEY`: Your OpenAI API key
- `OLLAMA_BASE_URL`: Ollama server URL (for local models)
- `LOG_LEVEL`: Logging verbosity (DEBUG, INFO, WARNING, ERROR)
- `MAX_PAGES_PER_STATEMENT`: Processing limits
- `OUTPUT_DIR`: Default output directory

See [Configuration Guide](docs/getting-started/configuration.md) for complete details.

## 🏗 Architecture

The system consists of several key components:

- **Workflow Engine**: LangGraph-based state machine for processing steps
- **LLM Analyzer**: AI-powered boundary detection and metadata extraction
- **PDF Processor**: Document manipulation and text extraction
- **Error Handler**: Comprehensive error management and recovery
- **Rate Limiter**: API usage controls and backoff mechanisms

### Processing Pipeline

1. **PDF Ingestion**: Load and validate input documents
2. **Document Analysis**: Extract text and structural information
3. **Statement Detection**: AI boundary detection using LLM analysis
4. **Metadata Extraction**: Account and period information extraction
5. **PDF Generation**: Create individual statement files
6. **File Organization**: Apply naming conventions and organization

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src

# Run specific test categories
uv run pytest tests/unit/
uv run pytest tests/integration/
```

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Install development dependencies: `uv sync --group dev`
4. Make your changes
5. Run tests: `uv run pytest`
6. Format code: `uv run ruff format .`
7. Check linting: `uv run ruff check .`
8. Commit your changes with a descriptive message
9. Push to your fork and create a pull request

### Code Quality

- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Write comprehensive docstrings for public APIs
- Add tests for new features and bug fixes
- Keep functions focused and small
- Use descriptive variable and function names

### Pull Request Process

1. Ensure all tests pass
2. Update documentation if needed
3. Add appropriate commit trailers (see below)
4. Request review from maintainers

### Commit Guidelines

For commits fixing bugs or adding features based on user reports:
```bash
git commit --trailer "Reported-by:<name>"
```

For commits related to a GitHub issue:
```bash
git commit --trailer "Github-Issue:#<number>"
```

## 📚 Documentation

📖 **[Read the full documentation online](https://madeinoz67.github.io/bank-statement-separator/)**

Complete documentation is available in the `docs/` directory:

- [Getting Started](docs/getting-started/)
- [User Guide](docs/user-guide/)
- [Developer Guide](docs/developer-guide/)
- [API Reference](docs/reference/)
- [Architecture](docs/architecture/)

Build documentation locally:
```bash
uv run mkdocs serve
```

## 📦 Dependencies

### Core Dependencies

- `langchain`: LLM integration framework
- `langgraph`: Stateful workflow orchestration
- `pymupdf`: PDF processing
- `pydantic`: Data validation
- `rich`: Terminal formatting
- `python-dotenv`: Environment management

### Development Dependencies

- `pytest`: Testing framework
- `ruff`: Code formatting and linting
- `pyright`: Type checking
- `mkdocs`: Documentation generation

See `pyproject.toml` for complete dependency list.

## 🔒 Security

- API keys are managed through environment variables
- Input validation on all user-provided data
- Rate limiting for external API calls
- Comprehensive logging for audit trails
- No sensitive data stored in application logs

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [LangChain](https://langchain.com/) and [LangGraph](https://langchain-ai.github.io/langgraph/)
- PDF processing powered by [PyMuPDF](https://pymupdf.readthedocs.io/)
- Inspired by the need for automated document processing in financial workflows

## 🐛 Issues & Support

- Report bugs via [GitHub Issues](https://github.com/madeinoz67/bank-statement-separator/issues)
- Check [Troubleshooting Guide](docs/reference/troubleshooting.md) for common issues
- Review [Known Issues](docs/known_issues/) for current limitations

---

**Note**: This tool requires an OpenAI API key for AI functionality. Falls back to pattern matching if LLM is unavailable.
