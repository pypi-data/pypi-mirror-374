"""Configuration service package."""

from kp_ssf_tools.core.services.config.interfaces import (
    ConfigurationManagerProtocol,
    ConfigurationServiceProtocol,
)
from kp_ssf_tools.core.services.config.manager import ConfigurationManager
from kp_ssf_tools.core.services.config.service import ConfigurationService

__all__: list[str] = [
    "ConfigurationManager",
    "ConfigurationManagerProtocol",
    "ConfigurationService",
    "ConfigurationServiceProtocol",
]
