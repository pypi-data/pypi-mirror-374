"""Entropy analysis container for dependency injection."""

from __future__ import annotations

from typing import TYPE_CHECKING

from dependency_injector import containers, providers

from kp_ssf_tools.analyze.services import ContentAwareThresholdManager

if TYPE_CHECKING:
    from kp_ssf_tools.analyze.services import (
        ThresholdProviderProtocol,
    )
    from kp_ssf_tools.analyze.services.entropy.analyzer import EntropyAnalyzer


class EntropyContainer(containers.DeclarativeContainer):
    """Container for entropy analysis services."""

    # Core services (injected from main container)
    core: providers.DependenciesContainer = providers.DependenciesContainer()

    threshold_manager: providers.Singleton[ThresholdProviderProtocol] = (
        providers.Singleton(
            ContentAwareThresholdManager,
        )
    )

    # Entropy analyzer with core services injected
    analyzer: providers.Factory[EntropyAnalyzer] = providers.Factory(
        "kp_ssf_tools.analyze.services.entropy.analyzer.EntropyAnalyzer",
        rich_output=core.rich_output,
        timestamp_service=core.timestamp,
        file_validator=core.file_validator,
        mime_detector=core.mime_detector,
        file_processing=core.file_processing,
        threshold_manager=threshold_manager,
    )
