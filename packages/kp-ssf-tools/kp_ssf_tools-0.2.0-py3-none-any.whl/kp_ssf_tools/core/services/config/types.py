"""Type definitions for configuration services."""

from typing import TypeVar

from kp_ssf_tools.models.base import SSFToolsBaseModel
from kp_ssf_tools.models.types import PathLike

# Core configuration data types
type ConfigDict = dict[str, str | int | bool | float | list[object] | dict[str, object]]
type ConfigOverrides = ConfigDict | None

# Raw configuration section data (potentially invalid)
type ConfigSectionData = object  # Could be dict, list, str, or any YAML value

# Type variable for generic configuration models
ConfigT = TypeVar("ConfigT", bound=SSFToolsBaseModel)

# Path and source types
type ConfigPath = PathLike  # Path to configuration files
type ConfigSource = str  # Source identifier (file, cli, default, etc.)

__all__: list[str] = [
    "ConfigDict",
    "ConfigOverrides",
    "ConfigPath",
    "ConfigSectionData",
    "ConfigSource",
    "ConfigT",
]
