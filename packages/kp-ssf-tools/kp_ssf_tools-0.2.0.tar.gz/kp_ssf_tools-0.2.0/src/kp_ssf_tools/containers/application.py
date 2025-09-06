"""Main application container that wires all services together."""

from typing import TYPE_CHECKING, NamedTuple, cast

from dependency_injector import containers, providers

from kp_ssf_tools.analyze.models.configuration import AnalysisConfiguration
from kp_ssf_tools.containers.analysis import AnalysisContainer
from kp_ssf_tools.containers.core import CoreContainer
from kp_ssf_tools.core.services.config import ConfigurationManager, ConfigurationService
from kp_ssf_tools.core.services.config.models import GlobalConfiguration
from kp_ssf_tools.core.services.rich_output.service import RichOutputService

if TYPE_CHECKING:
    from kp_ssf_tools.core.services.config.interfaces import (
        ConfigurationServiceProtocol,
    )
    from kp_ssf_tools.models.base import SSFToolsBaseModel


def _configure_config_manager(
    manager: ConfigurationManager,
    global_service: ConfigurationService[GlobalConfiguration],
    entropy_service: ConfigurationService[AnalysisConfiguration],
) -> ConfigurationManager:
    """Configure the configuration manager with all available services."""
    # Register all command configuration services for unified config approach
    # Must use cast() to avoid mypy type safety warnings
    manager.register_command(
        "global",
        cast("ConfigurationServiceProtocol[SSFToolsBaseModel]", global_service),
    )
    manager.register_command(
        "entropy",
        cast("ConfigurationServiceProtocol[SSFToolsBaseModel]", entropy_service),
    )

    # Future commands will be registered here:
    # manager.register_command("volatility", volatility_service)
    # manager.register_command("forensics", forensics_service)

    return manager


class ConfigServices(NamedTuple):
    config_manager: "ConfigurationManager"
    rich_output: RichOutputService


class ApplicationContainer(containers.DeclarativeContainer):
    """Main application container that wires all services together."""

    # Configuration
    config = providers.Configuration()

    # Core services container
    core = providers.Container(
        CoreContainer,
        config=config,
    )

    # Configuration manager with services registered
    config_manager_configured: providers.Singleton[ConfigurationManager] = (
        providers.Singleton(
            _configure_config_manager,
            manager=core.config_manager,
            global_service=core.global_config_service,
            entropy_service=core.entropy_config_service,
        )
    )

    config_services: providers.Singleton[ConfigServices] = providers.Singleton(
        ConfigServices,
        config_manager=config_manager_configured,
        rich_output=core.rich_output,
    )

    # Analysis services container (entropy, wordlists, crypto detection)
    analysis = providers.Container(
        AnalysisContainer,
        core=core,
    )

    # For backward compatibility during transition
    entropy = analysis
