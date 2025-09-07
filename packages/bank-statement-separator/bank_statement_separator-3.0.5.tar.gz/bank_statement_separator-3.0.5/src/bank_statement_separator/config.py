"""Configuration management for bank statement separator."""

import os
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv


class Config(BaseModel):
    """Application configuration with validation and defaults."""

    # Core Configuration - LLM Provider Selection
    llm_provider: str = Field(
        default="openai", description="LLM provider to use (openai, ollama, auto)"
    )

    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(
        default=None, description="OpenAI API key for LLM operations"
    )
    openai_model: str = Field(default="gpt-4o-mini", description="OpenAI model to use")

    # Ollama Configuration
    ollama_base_url: str = Field(
        default="http://localhost:11434", description="Ollama base URL"
    )
    ollama_model: str = Field(default="llama3.2", description="Ollama model to use")

    # General LLM Configuration
    llm_temperature: float = Field(
        default=0.0, ge=0.0, le=2.0, description="LLM temperature"
    )
    llm_max_tokens: int = Field(
        default=4000, gt=0, description="Maximum tokens for LLM responses"
    )
    llm_fallback_enabled: bool = Field(
        default=True, description="Enable fallback between providers"
    )

    # Processing Configuration
    chunk_size: int = Field(
        default=6000, gt=0, description="Text chunk size for processing"
    )
    chunk_overlap: int = Field(
        default=800, ge=0, description="Overlap between text chunks"
    )
    max_filename_length: int = Field(
        default=240, gt=0, description="Maximum length for generated filenames"
    )
    default_output_dir: str = Field(
        default="./separated_statements", description="Default output directory"
    )
    processed_input_dir: Optional[str] = Field(
        default=None,
        description="Directory to move processed input files (uses input_dir/processed if None)",
    )

    # Security Configuration
    enable_audit_logging: bool = Field(default=True, description="Enable audit logging")
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: str = Field(
        default="./logs/statement_processing.log", description="Log file path"
    )
    allowed_input_dirs: Optional[List[str]] = Field(
        default=None, description="Allowed input directories"
    )
    allowed_output_dirs: Optional[List[str]] = Field(
        default=None, description="Allowed output directories"
    )
    max_file_size_mb: int = Field(
        default=100, gt=0, description="Maximum file size in MB"
    )

    # Advanced Configuration
    enable_fallback_processing: bool = Field(
        default=True, description="Enable fallback processing"
    )
    include_bank_in_filename: bool = Field(
        default=True, description="Include bank name in filename"
    )
    date_format: str = Field(default="YYYY-MM", description="Date format for filenames")
    max_pages_per_statement: int = Field(
        default=50, gt=0, description="Maximum pages per statement"
    )
    max_total_pages: int = Field(
        default=500, gt=0, description="Maximum total pages to process"
    )

    # Paperless-ngx Integration
    paperless_enabled: bool = Field(
        default=False, description="Enable paperless-ngx integration"
    )
    paperless_url: Optional[str] = Field(
        default=None, description="Paperless-ngx base URL"
    )
    paperless_token: Optional[str] = Field(
        default=None, description="Paperless-ngx API token"
    )
    paperless_tags: Optional[List[str]] = Field(
        default=None, description="Default tags for uploaded documents"
    )
    paperless_correspondent: Optional[str] = Field(
        default=None, description="Default correspondent name"
    )
    paperless_document_type: Optional[str] = Field(
        default=None, description="Default document type"
    )
    paperless_storage_path: Optional[str] = Field(
        default=None, description="Storage path name for uploaded documents"
    )

    # Error Handling Configuration
    quarantine_directory: Optional[str] = Field(
        default=None,
        description="Directory for failed/invalid documents (uses output_dir/quarantine if None)",
    )
    max_retry_attempts: int = Field(
        default=2,
        ge=0,
        le=5,
        description="Maximum retry attempts for transient failures",
    )
    continue_on_validation_warnings: bool = Field(
        default=True, description="Continue processing despite validation warnings"
    )
    auto_quarantine_critical_failures: bool = Field(
        default=True,
        description="Automatically quarantine documents with critical failures",
    )
    preserve_failed_outputs: bool = Field(
        default=True, description="Keep partial outputs when processing fails"
    )
    enable_error_reporting: bool = Field(
        default=True, description="Generate detailed error reports for failures"
    )
    error_report_directory: Optional[str] = Field(
        default=None,
        description="Directory for error reports (uses quarantine_dir if None)",
    )
    validation_strictness: str = Field(
        default="normal",
        pattern="^(strict|normal|lenient)$",
        description="Validation strictness level",
    )

    # Document Validation Configuration
    min_pages_per_statement: int = Field(
        default=1, gt=0, description="Minimum pages required per statement"
    )
    max_file_age_days: Optional[int] = Field(
        default=None,
        ge=1,
        description="Maximum age of input files in days (None for no limit)",
    )
    allowed_file_extensions: List[str] = Field(
        default=[".pdf"], description="Allowed file extensions for processing"
    )
    require_text_content: bool = Field(
        default=True, description="Require documents to contain extractable text"
    )
    min_text_content_ratio: float = Field(
        default=0.1,
        ge=0.0,
        le=1.0,
        description="Minimum ratio of pages with text content",
    )

    @validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level is one of the standard levels."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()

    @validator("openai_model")
    def validate_openai_model(cls, v):
        """Validate OpenAI model name."""
        valid_models = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo", "gpt-4-turbo"]
        if v not in valid_models:
            raise ValueError(f"OpenAI model must be one of: {valid_models}")
        return v

    @validator("llm_provider")
    def validate_llm_provider(cls, v):
        """Validate LLM provider name."""
        valid_providers = ["openai", "ollama", "auto"]
        if v not in valid_providers:
            raise ValueError(f"LLM provider must be one of: {valid_providers}")
        return v

    @validator("chunk_overlap")
    def validate_chunk_overlap(cls, v, values):
        """Ensure chunk overlap is less than chunk size."""
        if "chunk_size" in values and v >= values["chunk_size"]:
            raise ValueError("Chunk overlap must be less than chunk size")
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def load_config(env_file: Optional[str] = None) -> Config:
    """
    Load configuration from environment variables and .env file.

    Args:
        env_file: Optional path to .env file. If None, uses default .env

    Returns:
        Config: Validated configuration instance

    Raises:
        ValueError: If required configuration is missing or invalid
    """
    if env_file:
        load_dotenv(env_file)
    else:
        load_dotenv()

    # Convert environment variables to the format expected by Pydantic
    config_data = {}

    # Map environment variables to config fields
    env_mapping = {
        # LLM Provider Configuration
        "LLM_PROVIDER": "llm_provider",
        "OPENAI_API_KEY": "openai_api_key",
        "OPENAI_MODEL": "openai_model",
        "OLLAMA_BASE_URL": "ollama_base_url",
        "OLLAMA_MODEL": "ollama_model",
        "LLM_TEMPERATURE": "llm_temperature",
        "LLM_MAX_TOKENS": "llm_max_tokens",
        "LLM_FALLBACK_ENABLED": "llm_fallback_enabled",
        "CHUNK_SIZE": "chunk_size",
        "CHUNK_OVERLAP": "chunk_overlap",
        "MAX_FILENAME_LENGTH": "max_filename_length",
        "DEFAULT_OUTPUT_DIR": "default_output_dir",
        "PROCESSED_INPUT_DIR": "processed_input_dir",
        "ENABLE_AUDIT_LOGGING": "enable_audit_logging",
        "LOG_LEVEL": "log_level",
        "LOG_FILE": "log_file",
        "ALLOWED_INPUT_DIRS": "allowed_input_dirs",
        "ALLOWED_OUTPUT_DIRS": "allowed_output_dirs",
        "MAX_FILE_SIZE_MB": "max_file_size_mb",
        "ENABLE_FALLBACK_PROCESSING": "enable_fallback_processing",
        "INCLUDE_BANK_IN_FILENAME": "include_bank_in_filename",
        "DATE_FORMAT": "date_format",
        "MAX_PAGES_PER_STATEMENT": "max_pages_per_statement",
        "MAX_TOTAL_PAGES": "max_total_pages",
        "PAPERLESS_ENABLED": "paperless_enabled",
        "PAPERLESS_URL": "paperless_url",
        "PAPERLESS_TOKEN": "paperless_token",
        "PAPERLESS_TAGS": "paperless_tags",
        "PAPERLESS_CORRESPONDENT": "paperless_correspondent",
        "PAPERLESS_DOCUMENT_TYPE": "paperless_document_type",
        "PAPERLESS_STORAGE_PATH": "paperless_storage_path",
        # Error Handling
        "QUARANTINE_DIRECTORY": "quarantine_directory",
        "MAX_RETRY_ATTEMPTS": "max_retry_attempts",
        "CONTINUE_ON_VALIDATION_WARNINGS": "continue_on_validation_warnings",
        "AUTO_QUARANTINE_CRITICAL_FAILURES": "auto_quarantine_critical_failures",
        "PRESERVE_FAILED_OUTPUTS": "preserve_failed_outputs",
        "ENABLE_ERROR_REPORTING": "enable_error_reporting",
        "ERROR_REPORT_DIRECTORY": "error_report_directory",
        "VALIDATION_STRICTNESS": "validation_strictness",
        # Document Validation
        "MIN_PAGES_PER_STATEMENT": "min_pages_per_statement",
        "MAX_FILE_AGE_DAYS": "max_file_age_days",
        "ALLOWED_FILE_EXTENSIONS": "allowed_file_extensions",
        "REQUIRE_TEXT_CONTENT": "require_text_content",
        "MIN_TEXT_CONTENT_RATIO": "min_text_content_ratio",
    }

    for env_var, config_key in env_mapping.items():
        value = os.getenv(env_var)
        if value is not None:
            # Handle special cases for type conversion
            if config_key in [
                "allowed_input_dirs",
                "allowed_output_dirs",
                "paperless_tags",
                "allowed_file_extensions",
            ]:
                # Split comma-separated values into list
                config_data[config_key] = [
                    item.strip() for item in value.split(",") if item.strip()
                ]
            elif config_key in [
                "enable_audit_logging",
                "enable_fallback_processing",
                "include_bank_in_filename",
                "paperless_enabled",
            ]:
                # Convert string to boolean
                config_data[config_key] = value.lower() in ("true", "1", "yes", "on")
            elif config_key in ["llm_temperature"]:
                # Convert to float
                config_data[config_key] = float(value)
            elif config_key in [
                "llm_max_tokens",
                "chunk_size",
                "chunk_overlap",
                "max_filename_length",
                "max_file_size_mb",
                "max_pages_per_statement",
                "max_total_pages",
            ]:
                # Convert to int
                config_data[config_key] = int(value)
            else:
                config_data[config_key] = value

    return Config(**config_data)


def ensure_directories(config: Config) -> None:
    """
    Ensure required directories exist.

    Args:
        config: Configuration instance
    """
    # Create output directory
    Path(config.default_output_dir).mkdir(parents=True, exist_ok=True)

    # Create log directory
    log_dir = Path(config.log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)


def validate_file_access(
    file_path: str, config: Config, operation: str = "read"
) -> bool:
    """
    Validate file access against allowed directories.

    Args:
        file_path: Path to validate
        config: Configuration instance
        operation: Operation type ('read' or 'write')

    Returns:
        bool: True if access is allowed
    """
    path = Path(file_path).resolve()

    if operation == "read" and config.allowed_input_dirs:
        allowed_dirs = [Path(d).resolve() for d in config.allowed_input_dirs]
        return any(
            str(path).startswith(str(allowed_dir)) for allowed_dir in allowed_dirs
        )

    if operation == "write" and config.allowed_output_dirs:
        allowed_dirs = [Path(d).resolve() for d in config.allowed_output_dirs]
        return any(
            str(path).startswith(str(allowed_dir)) for allowed_dir in allowed_dirs
        )

    # If no restrictions configured, allow access
    return True
