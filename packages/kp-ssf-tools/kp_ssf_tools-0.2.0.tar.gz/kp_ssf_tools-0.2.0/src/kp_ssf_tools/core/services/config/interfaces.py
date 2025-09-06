"""Configuration service interfaces for dependency injection."""

from pathlib import Path
from typing import Protocol

from kp_ssf_tools.core.services.config.models import (
    ConfigurationSource,
    ValidationResult,
)
from kp_ssf_tools.core.services.config.types import (
    ConfigDict,
    ConfigOverrides,
    ConfigT,
)
from kp_ssf_tools.models.base import SSFToolsBaseModel


class ConfigurationServiceProtocol(Protocol[ConfigT]):
    """Protocol for configuration management - dependency injection compatible."""

    def load_config(
        self,
        config_path: Path | None = None,
        command_overrides: ConfigOverrides = None,
    ) -> ConfigT:
        """Load configuration from file with CLI overrides."""
        ...

    def save_config(self, config: ConfigT, config_path: Path) -> None:
        """Save configuration to file."""
        ...

    def validate_config(self, config: ConfigT | ConfigDict) -> ValidationResult:
        """Validate configuration and return detailed results."""
        ...

    def create_default_config(self, command: str) -> ConfigT:
        """Create default configuration for specific command."""
        ...

    def merge_configurations(self, base: ConfigT, overrides: ConfigDict) -> ConfigT:
        """Merge configuration with runtime overrides."""
        ...

    def get_config_paths(self) -> list[Path]:
        """Get standard configuration file paths."""
        ...

    def discover_config_files(
        self,
        search_paths: list[Path],
    ) -> list[ConfigurationSource]:
        """Discover configuration files in search paths."""
        ...


class ConfigurationManagerProtocol(Protocol):
    """Protocol for managing multiple configuration types."""

    def get_service(
        self,
        command: str,
    ) -> ConfigurationServiceProtocol[SSFToolsBaseModel]:
        """Get configuration service for any supported command."""
        ...

    def list_available_commands(self) -> list[str]:
        """List commands with configuration support."""
        ...

    def register_command(
        self,
        command: str,
        service: ConfigurationServiceProtocol[SSFToolsBaseModel],
    ) -> None:
        """Register a configuration service for a command."""
        ...

    def is_command_supported(self, command: str) -> bool:
        """Check if a command has configuration support."""
        ...

    def validate_command_config(
        self,
        command: str,
        config_data: ConfigDict,
    ) -> ValidationResult:
        """Validate configuration for a specific command without importing models."""
        ...

    def get_effective_config(
        self,
        command: str,
        user_config_path: Path | None = None,
        project_config_path: Path | None = None,
        cli_overrides: ConfigOverrides = None,
    ) -> ConfigDict:
        """Get effective configuration merged from all sources as dict."""
        ...

    def extract_cli_overrides(
        self,
        param_mapping: dict[str, tuple[str, str]],
    ) -> ConfigDict:
        """
        Extract CLI parameter overrides using a mapping table.

        Args:
            param_mapping: Dict mapping CLI param names to (config_section, config_key) tuples

        Returns:
            ConfigDict suitable for passing to get_effective_config as cli_overrides

        """
        ...
