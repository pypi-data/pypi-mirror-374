"""Configuration models for AIMCP."""

from enum import StrEnum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class TransportType(StrEnum):
    """MCP server transport types."""

    STDIO = "stdio"
    HTTP = "http"
    SSE = "sse"


class LogLevel(StrEnum):
    """Log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class CacheBackend(StrEnum):
    """Cache backend types."""

    MEMORY = "memory"
    FILE = "file"


class ServerConfig(BaseModel):
    """Server configuration."""

    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8000, ge=1, le=65535, description="Server port (1-65535)")
    transport: TransportType = Field(default=TransportType.STDIO)
    name: str = Field(default="AIMCP")


class GitLabRepository(BaseModel):
    """GitLab repository configuration."""

    model_config = {"frozen": True}

    url: str
    branch: str = "main"

    @field_validator("url")
    @classmethod
    def clean_repository_url(cls, v: str) -> str:
        """Clean up repository URL by removing leading and trailing slashes."""
        return v.strip("/")


class GitLabConfig(BaseModel):
    """GitLab API configuration."""

    instance_url: HttpUrl
    token: str
    repositories: list[GitLabRepository]
    timeout: int = 30
    max_retries: int = 3

    @field_validator("token")
    @classmethod
    def validate_token(cls, v: str) -> str:
        """Validate GitLab token is not empty."""
        if not v.strip():
            exc_message = "GitLab token is required and cannot be empty"
            raise ValueError(exc_message)
        return v.strip()

    @field_validator("repositories")
    @classmethod
    def validate_repositories(cls, v: list[GitLabRepository]) -> list[GitLabRepository]:
        """Validate at least one repository is configured."""
        if not v:
            exc_message = "At least one GitLab repository must be configured"
            raise ValueError(exc_message)
        return v


class CacheConfig(BaseModel):
    """Cache configuration."""

    backend: CacheBackend = CacheBackend.MEMORY
    ttl_seconds: int = 3600
    max_size: int = 1000
    storage_path: Path | None = None

    @model_validator(mode="after")
    def validate_file_backend(self) -> "CacheConfig":
        """Validate file backend configuration."""
        if self.backend == CacheBackend.FILE and not self.storage_path:
            exc_message = "Storage path is required for file-based cache"
            raise ValueError(exc_message)
        return self


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: LogLevel = LogLevel.INFO
    structured: bool = True
    format: str | None = None


class ToolConfig(BaseModel):
    """Tool processing configuration."""

    conflict_resolution_strategy: str = "prefix"
    max_file_size: int = 1024 * 1024
    encoding: str = "utf-8"
    max_auto_load_size: int = 10 * 1024  # 10KB default for auto-loading resources

    @field_validator("conflict_resolution_strategy")
    @classmethod
    def validate_conflict_strategy(cls, v: str) -> str:
        """Validate conflict resolution strategy."""
        allowed = {"prefix", "priority", "error", "merge"}
        if v not in allowed:
            exc_message = f"Conflict resolution strategy must be one of: {allowed}"
            raise ValueError(exc_message)
        return v


class AIMCPConfig(BaseSettings):
    """Main AIMCP configuration with file and environment support."""

    model_config = SettingsConfigDict(
        env_prefix="AIMCP_",
        env_nested_delimiter="__",
        case_sensitive=False,
        yaml_file="config.yaml",
        yaml_file_encoding="utf-8",
        validate_assignment=True,
    )

    server: ServerConfig = Field(default_factory=ServerConfig)
    gitlab: GitLabConfig
    cache: CacheConfig = Field(default_factory=CacheConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    tools: ToolConfig = Field(default_factory=ToolConfig)

    @classmethod
    def from_yaml_file(cls, file_path: Path, overrides: dict[str, Any] | None = None) -> "AIMCPConfig":
        """Create configuration from YAML file with optional overrides.

        Args:
            file_path: Path to YAML configuration file
            overrides: Optional dictionary of override values

        Returns:
            Validated configuration instance

        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is invalid YAML
            ValidationError: If configuration is invalid
        """
        if not file_path.exists():
            exc_message = f"Configuration file not found: {file_path}"
            raise FileNotFoundError(exc_message)

        try:
            with file_path.open("r", encoding="utf-8") as f:
                file_data = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            exc_message = f"Invalid YAML in config file {file_path}: {e}"
            raise yaml.YAMLError(exc_message) from e

        # Apply overrides if provided
        if overrides and any(k in overrides for k in ["host", "port", "transport"]):
            # Apply server overrides
            server_data = file_data.setdefault("server", {})
            for key in ["host", "port", "transport"]:
                if key in overrides:
                    server_data[key] = overrides[key]

        return cls.model_validate(file_data)

    @classmethod
    def create(cls, config_path: Path | None = None, overrides: dict[str, Any] | None = None) -> "AIMCPConfig":
        """Create configuration from file and environment with overrides.

        Args:
            config_path: Optional path to configuration file
            overrides: Optional settings to override

        Returns:
            Validated AIMCP configuration
        """
        if config_path:
            return cls.from_yaml_file(config_path, overrides)
        # Load from environment variables only
        config_data = overrides or {}
        return cls.model_validate(config_data)
