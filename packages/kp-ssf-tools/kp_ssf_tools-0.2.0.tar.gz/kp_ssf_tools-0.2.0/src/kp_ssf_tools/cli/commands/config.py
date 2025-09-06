"""CLI configuration management commands."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import rich_click as click
import yaml
from dependency_injector.wiring import Provide, inject

from kp_ssf_tools.containers.application import ApplicationContainer, ConfigServices
from kp_ssf_tools.core.services.rich_output.service import RichOutputService

if TYPE_CHECKING:
    from kp_ssf_tools.core.services.config.manager import ConfigurationManager
    from kp_ssf_tools.core.services.rich_output.service import RichOutputService


@click.group(name="config")
@click.pass_context
def config_group(ctx: click.Context) -> None:
    """Configuration management commands."""


@config_group.command("init")
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output configuration file path",
)
@click.option(
    "--user",
    is_flag=True,
    help="Create configuration in user config directory",
)
@click.option(
    "--overwrite",
    is_flag=True,
    help="Overwrite existing configuration",
)
@click.option(
    "--config-format",
    type=click.Choice(["yaml"]),
    default="yaml",
    help="Configuration format",
)
@inject
def init_config(
    output: str | None,
    *,
    user: bool,
    overwrite: bool,
    config_format: str,
    config_services: ConfigServices = Provide[ApplicationContainer.config_services],
) -> None:
    """Initialize unified configuration file for all registered commands."""
    # Get rich output service directly from container to reduce parameter count
    rich_output: RichOutputService = config_services.rich_output
    config_manager: ConfigurationManager = config_services.config_manager

    # Get all available commands
    available_commands = config_manager.list_available_commands()

    if not available_commands:
        rich_output.error("No commands are registered with the configuration manager")
        return

    # Create separate global configuration
    from kp_ssf_tools.core.services.config.models import GlobalConfiguration

    global_config = GlobalConfiguration()
    global_config_dict = global_config.model_dump(mode="json", exclude_none=True)

    # Determine output path
    if output:
        config_path = Path(output)
    elif user:
        # Use platform-independent user config directory
        try:
            from platformdirs import user_config_dir

            user_config_path = Path(user_config_dir("ssf-tools", "kirkpatrickprice"))
            user_config_path.mkdir(parents=True, exist_ok=True)
            config_path = user_config_path / f"ssf-tools-config.{config_format}"
        except ImportError:
            rich_output.error("platformdirs package is required for --user option")
            rich_output.info("Install with: pip install platformdirs")
            return
    else:
        config_path = Path.cwd() / f"ssf-tools-config.{config_format}"

    # Check for existing file
    if config_path.exists() and not overwrite:
        rich_output.error(f"Configuration file already exists: {config_path}")
        rich_output.info("Use --overwrite to replace existing file")
        return

    # Create unified config structure with global and all command sections
    unified_config = {"global": global_config_dict}

    # Add configuration for each registered command
    for command in available_commands:
        if command != "global":  # Skip global as it's already added
            command_config_dict = config_manager.create_default_config_for_command(
                command,
            )
            unified_config[command] = command_config_dict

    # Ensure parent directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Save configuration using YAML
    try:
        import yaml

        with config_path.open("w") as f:
            yaml.dump(unified_config, f, default_flow_style=False, indent=2)

        non_global_commands = [cmd for cmd in available_commands if cmd != "global"]
        if non_global_commands:
            command_list = ", ".join(sorted(non_global_commands))
            rich_output.success(
                f"Created unified configuration: global + {command_list} -> {config_path}",
            )
        else:
            rich_output.success(
                f"Created unified configuration with global section: {config_path}",
            )
    except (OSError, yaml.YAMLError) as e:
        rich_output.error(f"Failed to save configuration: {e}")


@config_group.command("validate")
@click.argument("config_path", type=click.Path(exists=True))
@inject
def validate_config(
    config_path: str,
    *,
    config_services: ConfigServices = Provide[ApplicationContainer.config_services],
) -> None:
    """Validate unified configuration file."""
    config_manager = config_services.config_manager
    rich_output = config_services.rich_output

    try:
        # Load the unified config file
        config_file_path = Path(config_path)

        with config_file_path.open("r") as f:
            config_data = yaml.safe_load(f)

        if not isinstance(config_data, dict):
            rich_output.error("Configuration file must contain a valid YAML dictionary")
            return

        # Validate all sections
        validation_result = _validate_all_sections(
            config_data,
            config_manager,
            config_file_path,
            rich_output,
        )

        # Report final result with appropriate color and message
        if validation_result["has_errors"]:
            rich_output.error("Configuration file has validation errors")
        elif validation_result["has_warnings"]:
            rich_output.warning(
                f"Configuration file is valid (with warnings): {config_path}",
            )
        else:
            rich_output.success(f"Configuration file is valid: {config_path}")

    except (OSError, yaml.YAMLError) as e:
        rich_output.error(f"Failed to validate configuration: {e}")


def _validate_all_sections(
    config_data: dict[str, object],
    config_manager: ConfigurationManager,
    config_file_path: Path,
    rich_output: RichOutputService,
) -> dict[str, bool]:
    """Validate all sections in the config data."""
    has_errors = False
    has_warnings = False
    available_commands = config_manager.list_available_commands()

    for section_name, section_data in config_data.items():
        if section_name in available_commands:
            section_result = _validate_single_section(
                section_name,
                section_data,
                config_manager,
                config_file_path,
                rich_output,
            )
            if not section_result["is_valid"]:
                has_errors = True
            if section_result["has_warnings"]:
                has_warnings = True
        else:
            rich_output.warning(
                f"? Unknown section '{section_name}' (not registered)",
            )
            has_warnings = True

    return {
        "has_errors": has_errors,
        "has_warnings": has_warnings,
    }


def _validate_single_section(
    section_name: str,
    section_data: object,
    config_manager: ConfigurationManager,
    config_file_path: Path,
    rich_output: RichOutputService,
) -> dict[str, bool]:
    """Validate a single configuration section."""
    try:
        service = config_manager.get_service(section_name)

        if hasattr(service, "validate_config"):
            return _validate_using_service_method(
                section_name,
                section_data,
                service,
                rich_output,
            )

        return _validate_using_load_method(
            section_name,
            service,
            config_file_path,
            rich_output,
        )

    except (ValueError, TypeError, AttributeError) as e:
        rich_output.error(
            f"✗ Section '{section_name}' validation failed: {e}",
        )
        return {"is_valid": False, "has_warnings": False}


def _validate_using_service_method(
    section_name: str,
    section_data: object,
    service: object,
    rich_output: RichOutputService,
) -> dict[str, bool]:
    """Validate using the service's validate_config method."""
    validation_result = service.validate_config(section_data)  # type: ignore[attr-defined]

    if validation_result.is_valid:
        rich_output.success(f"✓ Section '{section_name}' is valid")
    else:
        rich_output.error(f"✗ Section '{section_name}' has validation errors:")
        for error in validation_result.errors:
            rich_output.error(f"  - {error}")

    # Show warnings if any
    has_warnings = len(validation_result.warnings) > 0
    for warning in validation_result.warnings:
        rich_output.warning(f"  ! {warning}")

    return {
        "is_valid": validation_result.is_valid,
        "has_warnings": has_warnings,
    }


def _validate_using_load_method(
    section_name: str,
    service: object,
    config_file_path: Path,
    rich_output: RichOutputService,
) -> dict[str, bool]:
    """Validate using the service's load_config method as fallback."""
    service.load_config(config_file_path)  # type: ignore[attr-defined]
    rich_output.success(f"✓ Section '{section_name}' is valid")
    return {"is_valid": True, "has_warnings": False}


@config_group.command("show")
@click.option("--config", type=click.Path(), help="Configuration file path")
@inject
def show_config(
    config: str | None,
    *,
    config_services: ConfigServices = Provide[ApplicationContainer.config_services],
) -> None:
    """Show effective unified configuration (merged from all sources)."""
    config_manager = config_services.config_manager
    rich_output = config_services.rich_output

    try:
        # Get all registered commands
        available_commands = config_manager.list_available_commands()

        if not available_commands:
            rich_output.warning("No commands have configuration support registered")
            return

        # Determine if user wants a specific file or merged from all sources
        specific_config_path = Path(config) if config else None

        # Build effective merged configuration by loading through each service
        effective_config = _load_effective_config(
            config_manager,
            available_commands,
            specific_config_path,
            rich_output,
        )

        if not effective_config:
            rich_output.error("No valid configurations found")
            return

        # Display the results
        _display_effective_config(effective_config, specific_config_path, rich_output)

    except (OSError, yaml.YAMLError) as e:
        rich_output.error(f"Failed to load configuration: {e}")


def _resolve_config_path(config: str | None) -> Path | None:
    """Resolve configuration file path from options or defaults."""
    if config:
        return Path(config)

    # Look for config file in standard locations
    config_path = Path.cwd() / "ssf-tools-config.yaml"
    if config_path.exists():
        return config_path

    try:
        from platformdirs import user_config_dir

        user_config_path = Path(
            user_config_dir("ssf-tools", "kirkpatrickprice"),
        )
        return user_config_path / "ssf-tools-config.yaml"
    except ImportError:
        return None


def _load_effective_config(
    config_manager: ConfigurationManager,
    available_commands: list[str],
    config_path: Path | None,
    rich_output: RichOutputService,
) -> dict[str, object]:
    """Load effective configuration through each service for proper merging."""
    effective_config: dict[str, object] = {}

    for command in sorted(available_commands):
        try:
            service = config_manager.get_service(command)
            if hasattr(service, "load_config"):
                # Load config with proper merging - always use None to enable
                # multiple file merging unless a specific override is provided
                if config_path and config_path.exists():
                    # User specified a specific file, use that
                    loaded_config = service.load_config(config_path)
                else:
                    # Use automatic multi-file merging
                    loaded_config = service.load_config(None)

                # Convert to dict and clean up
                config_dict = loaded_config.model_dump(exclude_none=True)
                effective_config[command] = config_dict

        except (ValueError, TypeError, AttributeError) as e:
            rich_output.warning(f"Could not load config for '{command}': {e}")

    return effective_config


def _display_effective_config(
    effective_config: dict[str, object],
    config_path: Path | None,
    rich_output: RichOutputService,
) -> None:
    """Display the effective configuration with appropriate context."""
    config_yaml = yaml.dump(effective_config, default_flow_style=False, indent=2)

    # Show which sources were used
    if config_path and config_path.exists():
        rich_output.info(f"Configuration from single source: {config_path}")
    else:
        rich_output.info("Effective configuration (merged from all available sources)")

    rich_output.print_code(config_yaml, lexer="yaml")


@config_group.command("paths")
@inject
def show_paths(
    *,
    config_services: ConfigServices = Provide[ApplicationContainer.config_services],
) -> None:
    """Show unified configuration file search paths."""
    rich_output = config_services.rich_output

    # Get standard search paths for unified config
    search_paths = []

    # Current directory
    search_paths.append(Path.cwd() / "ssf-tools-config.yaml")

    # User config directory (if platformdirs available)
    try:
        from platformdirs import user_config_dir

        user_config_path = Path(user_config_dir("ssf-tools", "kirkpatrickprice"))
        search_paths.append(user_config_path / "ssf-tools-config.yaml")
    except ImportError:
        pass

    rich_output.info("Unified configuration file search paths:")
    for i, path in enumerate(search_paths, 1):
        status = "✓ exists" if path.exists() else "✗ not found"
        rich_output.print(f"  {i}. {path} ({status})")

    rich_output.info("\nUse 'ssf_tools config init' to create a configuration file")


@config_group.command("list")
@inject
def list_commands(
    *,
    config_services: ConfigServices = Provide[ApplicationContainer.config_services],
) -> None:
    """List all commands with configuration support."""
    config_manager = config_services.config_manager
    rich_output = config_services.rich_output

    available_commands = config_manager.list_available_commands()

    if not available_commands:
        rich_output.warning("No commands have configuration support registered")
        return

    rich_output.info("Commands with configuration support:")
    for command in sorted(available_commands):
        rich_output.print(f"  • {command}")

    rich_output.info(f"\nTotal: {len(available_commands)} command(s)")
    rich_output.info(
        "Use 'ssf_tools config init' to create a unified configuration file",
    )
