"""Configuration service implementation with dependency injection."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import TYPE_CHECKING, Generic

import yaml
from pydantic import ValidationError

from kp_ssf_tools.core.services.config.models import (
    ConfigurationFormat,
    ConfigurationScope,
    ConfigurationSource,
    ValidationResult,
)
from kp_ssf_tools.core.services.config.types import ConfigDict, ConfigOverrides, ConfigT

if TYPE_CHECKING:
    from kp_ssf_tools.core.services.rich_output.interfaces import RichOutputProtocol
    from kp_ssf_tools.core.services.timestamp.interfaces import TimestampProtocol


class ConfigurationService(Generic[ConfigT]):
    """Configuration service implementation with dependency injection."""

    def __init__(
        self,
        config_model: type[ConfigT],
        rich_output: RichOutputProtocol,
        timestamp_service: TimestampProtocol,
        config_section: str,
    ) -> None:
        """
        Initialize configuration service.

        Args:
            config_model: Pydantic model class for this configuration type
            rich_output: Rich output service for user feedback
            timestamp_service: Timestamp service for configuration metadata
            config_section: Section name in unified config file (e.g., "entropy", "volatility")

        """
        self._config_model: type[ConfigT] = config_model
        self._rich_output: RichOutputProtocol = rich_output
        self._timestamp_service: TimestampProtocol = timestamp_service
        self._config_section: str = config_section

    def load_config(
        self,
        config_path: Path | None = None,
        command_overrides: ConfigOverrides = None,
    ) -> ConfigT:
        """
        Load configuration from unified config file(s) with CLI overrides.

        Args:
            config_path: Path to unified configuration file (None for default search)
            command_overrides: CLI overrides to apply

        Returns:
            Loaded and merged configuration for this service's section

        """
        # Load and merge from multiple config files if no specific path provided
        if config_path is None:
            unified_config_data = self._load_and_merge_multiple_configs()
        elif config_path.exists():
            # Load from single specified file
            unified_config_data = self._load_file(config_path)
        else:
            unified_config_data = {}

        # Merge global and section-specific settings
        merged_config_data = self._merge_global_and_section_config(unified_config_data)

        # Create configuration instance
        try:
            config = self._config_model(**merged_config_data)
            if config_path is None:
                self._rich_output.debug(
                    f"Loaded {self._config_section} configuration from multiple sources with global settings merged",
                )
            else:
                self._rich_output.debug(
                    f"Loaded {self._config_section} configuration with global settings merged from {config_path}",
                )
        except ValidationError as e:
            self._rich_output.error(
                f"Invalid {self._config_section} configuration: {e}",
            )
            config = self.create_default_config(self._config_section)
        except (TypeError, ValueError) as e:
            self._rich_output.error(
                f"Failed to load {self._config_section} configuration: {e}",
            )
            config = self.create_default_config(self._config_section)

        # Apply command-line overrides
        if command_overrides:
            config = self.merge_configurations(config, command_overrides)
            self._rich_output.debug("Applied command-line overrides")

        return config

    def save_config(self, config: ConfigT, config_path: Path) -> None:
        """
        Save configuration to unified config file.

        Args:
            config: Configuration to save
            config_path: Target file path

        """
        # Ensure directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing unified config or create new structure
        if config_path.exists():
            try:
                unified_config = self._load_file(config_path)
            except RuntimeError:
                # If file is corrupt, start fresh
                unified_config = {}
        else:
            unified_config = {}

        # Prepare section config
        section_config_dict = config.model_dump()

        # Add timestamp if config has created_at field
        if (
            hasattr(config, "created_at")
            and section_config_dict.get("created_at") is None
        ):
            section_config_dict["created_at"] = self._timestamp_service.format_iso(
                self._timestamp_service.utc_now(),
            )

        # Update the specific section in unified config
        unified_config[self._config_section] = section_config_dict

        # Save unified config as YAML
        try:
            with config_path.open("w", encoding="utf-8") as f:
                yaml.safe_dump(
                    unified_config,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                )
            self._rich_output.success(
                f"Configuration saved to {config_path} (section: {self._config_section})",
            )
        except Exception as e:
            msg = f"Failed to save configuration to {config_path}: {e}"
            self._rich_output.error(msg)
            raise RuntimeError(msg) from e

    def validate_config(self, config: ConfigT | ConfigDict) -> ValidationResult:
        """
        Validate configuration and return detailed results.

        Args:
            config: Configuration to validate (model instance or dict)

        Returns:
            Validation result with errors, warnings, and deprecated fields

        """
        errors: list[str] = []
        warnings: list[str] = []
        deprecated_fields: list[str] = []

        try:
            # If it's a dict, try to create model instance
            if isinstance(config, dict):
                self._config_model(**config)
                self._rich_output.debug("Configuration validation passed")
            else:
                # Already a model instance, validate by re-creating
                self._config_model(**config.model_dump())
                self._rich_output.debug("Configuration model validation passed")

        except ValidationError as e:
            for error in e.errors():
                field_path = " -> ".join(str(loc) for loc in error["loc"])
                error_msg = f"{field_path}: {error['msg']}"
                errors.append(error_msg)
                self._rich_output.debug(f"Validation error: {error_msg}")

        except TypeError as e:
            errors.append(f"Type error during validation: {e}")
            self._rich_output.error(f"Type error during validation: {e}")

        # Check for deprecated fields (this would be extended based on actual deprecations)
        config_data = config if isinstance(config, dict) else config.model_dump()

        # Add logic here to check for deprecated field names
        # This is a placeholder for future deprecation handling
        deprecated_candidates: list[str] = []  # Add known deprecated fields as needed
        for field in deprecated_candidates:
            if field in config_data:
                deprecated_fields.append(field)
                warnings.append(f"Field '{field}' is deprecated")

        is_valid = len(errors) == 0

        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            deprecated_fields=deprecated_fields,
        )

    def create_default_config(self, section: str) -> ConfigT:
        """
        Create default configuration for specific section.

        Args:
            section: Configuration section name (used for metadata)

        Returns:
            Default configuration instance

        """
        try:
            config = self._config_model()
        except Exception as e:
            msg = f"Failed to create default configuration for {section}: {e}"
            self._rich_output.error(msg)
            raise RuntimeError(msg) from e
        else:
            self._rich_output.debug(f"Created default configuration for {section}")
            return config

    def merge_configurations(self, base: ConfigT, overrides: ConfigDict) -> ConfigT:
        """
        Merge configuration with runtime overrides.

        Args:
            base: Base configuration
            overrides: Override values to apply

        Returns:
            Merged configuration

        """
        try:
            # Convert base to dict for merging
            base_dict = base.model_dump()

            # Deep merge the overrides
            merged_dict = self._deep_merge(base_dict, overrides)

            # Create new instance with merged data
            merged_config = self._config_model(**merged_dict)
        except ValidationError as e:
            msg = f"Merged configuration is invalid: {e}"
            self._rich_output.error(msg)
            raise ValueError(msg) from e
        except Exception as e:
            msg = f"Failed to merge configurations: {e}"
            self._rich_output.error(msg)
            raise RuntimeError(msg) from e
        else:
            self._rich_output.debug("Successfully merged configurations")
            return merged_config

    def get_config_paths(self) -> list[Path]:
        """
        Get standard configuration file paths for unified ssf-tools config (platform-independent).

        Returns:
            List of paths in priority order (highest to lowest)

        """
        from platformdirs import user_config_dir

        config_filename = "ssf-tools-config.yaml"

        paths = [
            # 1. Current directory (project-specific) - highest priority
            Path.cwd() / config_filename,
            # 2. User config directory (platform-independent) - lower priority
            Path(user_config_dir("ssf_tools", "kirkpatrickprice")) / config_filename,
        ]

        self._rich_output.debug(
            f"Configuration search paths: {[str(p) for p in paths]}",
        )
        return paths

    def discover_config_files(
        self,
        search_paths: list[Path],
    ) -> list[ConfigurationSource]:
        """
        Discover configuration files in search paths.

        Args:
            search_paths: Paths to search for configuration files

        Returns:
            List of discovered configuration sources

        """
        sources: list[ConfigurationSource] = []

        for i, path in enumerate(search_paths):
            if path.exists() and path.is_file():
                try:
                    # Determine scope based on path location
                    if path.parent == Path.cwd():
                        scope = ConfigurationScope.PROJECT
                    else:
                        scope = ConfigurationScope.USER

                    source = ConfigurationSource(
                        path=path,
                        scope=scope,
                        format=ConfigurationFormat.YAML,
                        priority=len(search_paths) - i,  # Higher index = lower priority
                        last_modified=path.stat().st_mtime,
                        is_default=False,
                    )
                    sources.append(source)
                    self._rich_output.debug(
                        f"Discovered config: {path} (scope: {scope})",
                    )

                except (OSError, PermissionError) as e:
                    self._rich_output.warning(
                        f"Could not process config file {path}: {e}",
                    )

        return sources

    def _load_file(self, config_path: Path) -> ConfigDict:
        """
        Load configuration data from file (YAML only).

        Args:
            config_path: Path to configuration file

        Returns:
            Configuration data as dictionary

        Raises:
            RuntimeError: If file cannot be loaded or parsed

        """
        try:
            with config_path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if data is None:
                data = {}

            if not isinstance(data, dict):
                msg = f"Configuration file {config_path} must contain a YAML object, not {type(data).__name__}"
                raise TypeError(msg)

        except yaml.YAMLError as e:
            msg = f"Invalid YAML in {config_path}: {e}"
            self._rich_output.error(msg)
            raise RuntimeError(msg) from e
        except OSError as e:
            msg = f"Failed to load configuration from {config_path}: {e}"
            self._rich_output.error(msg)
            raise RuntimeError(msg) from e
        else:
            self._rich_output.debug(
                f"Loaded {len(data)} configuration items from {config_path}",
            )
            return data

    def _load_and_merge_multiple_configs(self) -> ConfigDict:
        """
        Load and merge configuration data from multiple config files in priority order.

        Returns:
            Merged configuration data from all available config files.
            Higher priority files override lower priority ones.

        """
        config_paths = self.get_config_paths()
        merged_data: ConfigDict = {}

        # Load files in reverse priority order (lowest to highest)
        # so higher priority files override lower priority ones
        for config_path in reversed(config_paths):
            if config_path.exists():
                try:
                    file_data = self._load_file(config_path)
                    # Deep merge this file's data into the accumulated data
                    merged_data = self._deep_merge(merged_data, file_data)
                    self._rich_output.debug(
                        f"Merged configuration from {config_path}",
                    )
                except RuntimeError:
                    # Skip files that can't be loaded (already logged in _load_file)
                    self._rich_output.warning(
                        f"Skipping corrupted config file: {config_path}",
                    )
                    continue

        return merged_data

    def _merge_global_and_section_config(
        self,
        unified_config_data: ConfigDict,
    ) -> ConfigDict:
        """
        Merge global and section-specific configuration data.

        Only merges fields that are compatible with the target model.

        Args:
            unified_config_data: The complete unified config file data

        Returns:
            Merged configuration dictionary with only valid fields
            for this section's configuration model

        """
        from typing import cast

        # Get section-specific settings (if they exist and are a dict)
        section_data_raw = unified_config_data.get(self._config_section, {})
        section_data: ConfigDict = cast(
            "ConfigDict",
            section_data_raw if isinstance(section_data_raw, dict) else {},
        )

        # For global section, return its own data directly
        if self._config_section == "global":
            return section_data

        # For other sections, start with section data
        result = copy.deepcopy(section_data)

        # Get global settings that are compatible with this model
        global_data_raw = unified_config_data.get("global", {})
        global_data: ConfigDict = cast(
            "ConfigDict",
            global_data_raw if isinstance(global_data_raw, dict) else {},
        )

        # Only merge global fields that are actually valid for this model
        # We do this by getting the model's field names and only merging those
        model_fields = set(self._config_model.model_fields.keys())

        for key, value in global_data.items():
            # Only merge if:
            # 1. The target model has this field
            # 2. The section-specific config doesn't already override it
            if key in model_fields and key not in result:
                result[key] = copy.deepcopy(value)

        return result

    def _deep_merge(self, base: ConfigDict, overrides: ConfigDict) -> ConfigDict:
        """
        Deep merge dictionaries.

        Args:
            base: Base dictionary
            overrides: Override dictionary

        Returns:
            Merged dictionary

        """
        result = copy.deepcopy(base)

        for key, value in overrides.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                # Recursively merge nested dictionaries
                result[key] = self._deep_merge(  # type: ignore[assignment]
                    result[key],  # type: ignore[arg-type]
                    value,  # type: ignore[arg-type]
                )
            else:
                # Override or add new value
                result[key] = copy.deepcopy(value)

        return result
