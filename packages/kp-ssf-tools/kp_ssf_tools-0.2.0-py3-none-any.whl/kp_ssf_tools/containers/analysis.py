"""Analysis container for dependency injection."""

from __future__ import annotations

from typing import TYPE_CHECKING

from dependency_injector import containers, providers

from kp_ssf_tools.analyze.services import ContentAwareThresholdManager
from kp_ssf_tools.analyze.services.detect_secrets_service import (
    DetectSecretsCredentialService,
)

if TYPE_CHECKING:
    from kp_ssf_tools.analyze.services import (
        ThresholdProviderProtocol,
    )
    from kp_ssf_tools.analyze.services.entropy.analyzer import EntropyAnalyzer


class AnalysisContainer(containers.DeclarativeContainer):
    """Container for analysis services (entropy, wordlists, crypto detection)."""

    # Core services (injected from main container)
    core: providers.DependenciesContainer = providers.DependenciesContainer()

    threshold_manager: providers.Singleton[ThresholdProviderProtocol] = (
        providers.Singleton(
            ContentAwareThresholdManager,
        )
    )

    # Entropy analyzer with core services injected
    entropy_analyzer: providers.Factory[EntropyAnalyzer] = providers.Factory(
        "kp_ssf_tools.analyze.services.entropy.analyzer.EntropyAnalyzer",
        rich_output=core.rich_output,
        timestamp_service=core.timestamp,
        file_validator=core.file_validator,
        mime_detector=core.mime_detector,
        file_processing=core.file_processing,
        threshold_manager=threshold_manager,
    )

    # Detect-secrets based credential service
    detect_secrets_credential_service: providers.Singleton[
        DetectSecretsCredentialService
    ] = providers.Singleton(
        DetectSecretsCredentialService,
        rich_output=core.rich_output,
        timestamp_service=core.timestamp,
        file_discovery=core.file_discoverer,
        file_processing=core.file_processing,
    )

    # Active credential detection service
    active_credential_service = detect_secrets_credential_service  # type: ignore[assignment]

    # For backward compatibility during transition
    analyzer = entropy_analyzer
