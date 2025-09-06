"""Configuration manager with registry pattern to avoid circular dependencies."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import click

from kp_ssf_tools.core.services.config.models import ValidationResult

if TYPE_CHECKING:
    from pathlib import Path

    from kp_ssf_tools.core.services.config.interfaces import (
        ConfigurationServiceProtocol,
    )
    from kp_ssf_tools.core.services.config.types import ConfigDict
    from kp_ssf_tools.models.base import SSFToolsBaseModel


class ConfigurationManager:
    """
    Registry-based configuration manager avoiding circular dependencies.

    Commands register their configuration services at runtime,
    allowing the core config service to validate and merge configurations
    without importing command-specific models.
    """

    def __init__(self) -> None:
        self._services: dict[str, ConfigurationServiceProtocol[Any]] = {}

    def get_service(
        self,
        command: str,
    ) -> ConfigurationServiceProtocol[Any]:
        """Get configuration service for any supported command."""
        if not self.is_command_supported(command):
            msg = f"No configuration service registered for command: {command}"
            raise ValueError(msg)
        return self._services[command]

    def list_available_commands(self) -> list[str]:
        """List commands with configuration support."""
        return list(self._services.keys())

    def register_command(
        self,
        command: str,
        service: ConfigurationServiceProtocol[Any],
    ) -> None:
        """Register a configuration service for a command."""
        self._services[command] = service

    def is_command_supported(self, command: str) -> bool:
        """Check if a command has configuration support."""
        return command in self._services

    def validate_command_config(
        self,
        command: str,
        config_data: ConfigDict,
    ) -> ValidationResult:
        """
        Validate configuration for a specific command.

        Uses the registered service to validate without importing models.
        """
        if not self.is_command_supported(command):
            return ValidationResult(
                is_valid=False,
                errors=[f"Command '{command}' is not supported"],
                warnings=[],
                deprecated_fields=[],
            )

        service: ConfigurationServiceProtocol[SSFToolsBaseModel] = self.get_service(
            command,
        )
        return service.validate_config(config_data)

    def get_effective_config(
        self,
        command: str,
        user_config_path: Path | None = None,
        project_config_path: Path | None = None,
        cli_overrides: ConfigDict | None = None,
    ) -> ConfigDict:
        """
        Get effective configuration merged from all sources.

        Returns a dict to avoid importing specific config models.
        """
        if not self.is_command_supported(command):
            msg = f"Command '{command}' is not supported"
            raise ValueError(msg)

        service: ConfigurationServiceProtocol[SSFToolsBaseModel] = self.get_service(
            command,
        )

        # Load base configuration
        config: SSFToolsBaseModel = service.create_default_config(command)

        # Load user-level config if exists
        if user_config_path and user_config_path.exists():
            user_config: SSFToolsBaseModel = service.load_config(user_config_path)
            config = service.merge_configurations(config, user_config.model_dump())

        # Load project-level config if exists
        if project_config_path and project_config_path.exists():
            project_config: SSFToolsBaseModel = service.load_config(project_config_path)
            config = service.merge_configurations(config, project_config.model_dump())

        # Apply CLI overrides
        if cli_overrides:
            config = service.merge_configurations(config, cli_overrides)

        return config.model_dump()

    def create_default_config_for_command(self, command: str) -> ConfigDict:
        """Create default configuration for a command as dict."""
        if not self.is_command_supported(command):
            msg = f"Command '{command}' is not supported"
            raise ValueError(msg)

        service: ConfigurationServiceProtocol[SSFToolsBaseModel] = self.get_service(
            command,
        )
        default_config: SSFToolsBaseModel = service.create_default_config(command)
        return default_config.model_dump(exclude_none=True)

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

        Example:
            param_mapping = {
                "block_size": ("analysis", "analysis_block_size"),
                "step_size": ("analysis", "step_size"),
            }

        The method uses click.get_current_context() to access CLI parameters.

        """
        ctx = click.get_current_context()
        cli_params = ctx.params

        overrides: ConfigDict = {}

        for cli_param, (section, key) in param_mapping.items():
            if cli_params.get(cli_param) is not None:
                if section not in overrides:
                    overrides[section] = {}
                # Cast to dict to satisfy type checker - we know this is a dict
                section_dict = overrides[section]
                if isinstance(section_dict, dict):
                    section_dict[key] = cli_params[cli_param]

        return overrides
