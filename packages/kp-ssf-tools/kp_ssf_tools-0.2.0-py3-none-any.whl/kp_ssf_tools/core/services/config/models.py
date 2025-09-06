from __future__ import annotations

from enum import StrEnum
from pathlib import Path

from pydantic import Field, field_validator

from kp_ssf_tools.models.base import SSFToolsBaseModel


class ConfigurationFormat(StrEnum):
    """Supported configuration file formats."""

    YAML = "yaml"


class ConfigurationScope(StrEnum):
    """Configuration scope levels."""

    USER = "user"  # User-specific settings
    PROJECT = "project"  # Project-specific settings
    RUNTIME = "runtime"  # Runtime CLI overrides


class OutputFormat(StrEnum):
    """Supported output formats."""

    XLSX = "xlsx"  # Default for results output
    YAML = "yaml"  # Added for config file output


class ConfigurationSource(SSFToolsBaseModel):
    """Configuration source metadata."""

    path: Path | None = Field(default=None, description="Path to configuration file")
    scope: ConfigurationScope = Field(description="Configuration scope level")
    format: ConfigurationFormat = Field(description="Configuration file format")
    priority: int = Field(description="Priority level (higher overrides lower)")
    last_modified: float | None = Field(
        default=None,
        description="Last modification timestamp",
    )
    is_default: bool = Field(
        default=False,
        description="Whether this is a default configuration",
    )


class ValidationResult(SSFToolsBaseModel):
    """Configuration validation results."""

    is_valid: bool = Field(description="Whether the configuration is valid")
    errors: list[str] = Field(default_factory=list, description="Validation errors")
    warnings: list[str] = Field(default_factory=list, description="Validation warnings")
    deprecated_fields: list[str] = Field(
        default_factory=list,
        description="Deprecated field names",
    )


class ConfigurationDisplaySettings(SSFToolsBaseModel):
    """Common output configuration settings."""

    format: str = Field(
        default="yaml",
        description="Output format for configuration display",
    )
    include_metadata: bool = Field(default=True, description="Include metadata")
    verbose: bool = Field(default=False, description="Verbose output")
    quiet: bool = Field(default=False, description="Suppress informational output")

    @field_validator("format")
    @classmethod
    def validate_format(cls, value: str) -> str:
        # Only YAML supported for configuration output
        if value != "yaml":
            msg: str = f"Invalid configuration output format: {value}"
            raise ValueError(msg)
        return value


class OutputConfig(SSFToolsBaseModel):
    """Output formatting configuration."""

    output_path: Path = Field(
        default=Path.cwd() / "results",
        description="Path to the output directory",
    )
    format: OutputFormat = OutputFormat.XLSX
    include_statistics: bool = True
    include_graphs: bool = False
    verbose: bool = False
    include_compliance_metadata: bool = False


class NetworkConfig(SSFToolsBaseModel):
    """Network operation configuration."""

    timeout_seconds: int = 10
    retry_count: int = 3
    offline_mode: bool = False


class BaseConfiguration(SSFToolsBaseModel):
    """Base configuration model with common fields."""

    version: str = Field(default="1.0", description="Configuration version")
    created_at: str | None = Field(
        default=None,
        description="Configuration creation timestamp",
    )
    description: str | None = Field(
        default=None,
        description="Configuration description",
    )


class GlobalConfiguration(BaseConfiguration):
    """Global SSF Tools configuration."""

    # These fields are used by all commands
    output: OutputConfig = Field(
        default_factory=OutputConfig,
        description="Output settings for all commands",
    )
    network: NetworkConfig = Field(
        default_factory=NetworkConfig,
        description="Network settings for all commands",
    )

    # Default paths (platform-independent using platformdirs)
    @staticmethod
    def _get_user_config_dir() -> Path:
        from platformdirs import user_config_dir

        return Path(user_config_dir("ssf_tools", "kirkpatrickprice"))

    @staticmethod
    def _get_cache_dir() -> Path:
        from platformdirs import user_cache_dir

        return Path(user_cache_dir("ssf_tools", "kirkpatrickprice"))

    @staticmethod
    def _get_default_log_dir() -> Path:
        from platformdirs import user_log_dir

        return Path(user_log_dir("ssf_tools", "kirkpatrickprice"))

    user_config_dir: Path = Field(
        default_factory=_get_user_config_dir,
        description="Default configuration directory",
    )
    cache_dir: Path = Field(
        default_factory=_get_cache_dir,
        description="Default cache directory",
    )
