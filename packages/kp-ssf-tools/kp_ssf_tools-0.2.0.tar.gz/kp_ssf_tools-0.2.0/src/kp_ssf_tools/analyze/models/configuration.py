"""Entropy-specific configuration models."""

from __future__ import annotations

from pydantic import Field

from kp_ssf_tools.analyze.models.content_aware import ContentAwareThresholds
from kp_ssf_tools.analyze.models.types import FileType
from kp_ssf_tools.core.services.config.models import BaseConfiguration
from kp_ssf_tools.models.base import SSFToolsBaseModel


class AnalysisConfig(SSFToolsBaseModel):
    """Analysis-specific configuration."""

    file_chunk_size: int = Field(
        default=8192,
        gt=0,
        description="File I/O chunk size in bytes - controls how much data is read from disk at once",
    )
    analysis_block_size: int = Field(
        default=64,
        gt=0,
        description="Analysis block size in bytes - controls the size of entropy analysis windows",
    )
    step_size: int = Field(
        default=16,
        gt=0,
        description="Step size for sliding window analysis",
    )


class ContentAwareConfig(SSFToolsBaseModel):
    """Content-aware analysis configuration for PCI SSF 2.3 compliance."""

    enabled: bool = True
    thresholds: ContentAwareThresholds = Field(
        default_factory=lambda: ContentAwareThresholds.for_file_type(
            FileType.DOCUMENTATION,
        ),
        description="File type-specific thresholds",
    )
    language_detection: bool = Field(
        default=True,
        description="Enable programming language detection",
    )


class DetectionConfig(SSFToolsBaseModel):
    """Detection feature configuration."""

    crypto_structures: bool = True
    credentials: bool = True
    credential_detection: bool = True
    statistical_analysis: bool = True


class CredentialConfig(SSFToolsBaseModel):
    """Credential detection configuration."""

    enabled: bool = True
    cache_duration_hours: int = Field(
        default=24,
        description="Hours to cache downloaded wordlists",
    )
    auto_download: bool = Field(
        default=True,
        description="Automatically download wordlists from SecLists",
    )
    wordlist_sources: dict[str, str] = Field(
        default_factory=lambda: {
            "usernames": "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Usernames/Names/names.txt",
            "xato_passwords": "https://github.com/danielmiessler/SecLists/raw/refs/heads/master/Passwords/Common-Credentials/xato-net-10-million-passwords-100000.txt",
            "ncsc_passwords": "https://github.com/danielmiessler/SecLists/raw/refs/heads/master/Passwords/Common-Credentials/100k-most-used-passwords-NCSC.txt",
        },
        description="Wordlist source URLs from SecLists repository",
    )


class StatisticalConfig(SSFToolsBaseModel):
    """Statistical analysis configuration."""

    normality_tests: list[str] = Field(
        default_factory=lambda: ["shapiro", "anderson", "kstest"],
    )
    outlier_detection: bool = True
    confidence_level: float = 0.95


class ComplianceConfig(SSFToolsBaseModel):
    """Compliance-specific configuration."""

    required_checks: list[str] = Field(
        default_factory=lambda: [
            "crypto_structures",
            "credentials",
            "entropy_analysis",
        ],
        description="Required compliance checks for PCI SSF 2.3",
    )
    generate_evidence: bool = Field(
        default=True,
        description="Generate audit trail evidence",
    )
    executive_summary: bool = Field(
        default=False,
        description="Generate executive summary",
    )


class ReportingConfig(SSFToolsBaseModel):
    """Reporting configuration for compliance."""

    risk_assessment: bool = True
    detailed_findings: bool = True
    include_samples: bool = Field(
        default=False,
        description="Include data samples in reports (sanitized)",
    )
    max_sample_length: int = Field(
        default=64,
        gt=0,
        description="Maximum length of data samples",
    )


class AnalysisConfiguration(BaseConfiguration):
    """
    Complete security analysis configuration.

    Inherits common output and network settings from BaseConfiguration.
    Contains analysis-specific configuration options for entropy analysis,
    wordlist detection, and cryptographic structure detection.
    """

    # Entropy-specific settings
    analysis: AnalysisConfig = Field(
        default_factory=AnalysisConfig,
        description="Analysis-specific settings",
    )

    # Content-aware thresholds
    content_aware: ContentAwareConfig = Field(
        default_factory=ContentAwareConfig,
        description="Content-aware analysis settings",
    )

    # Detection settings
    detection: DetectionConfig = Field(
        default_factory=DetectionConfig,
        description="Detection feature toggles",
    )

    # Credential detection
    credentials: CredentialConfig = Field(
        default_factory=CredentialConfig,
        description="Credential detection settings",
    )

    # Statistical analysis
    statistical: StatisticalConfig = Field(
        default_factory=StatisticalConfig,
        description="Statistical analysis settings",
    )

    # Compliance settings
    compliance: ComplianceConfig = Field(
        default_factory=ComplianceConfig,
        description="PCI SSF compliance settings",
    )

    # Reporting settings
    reporting: ReportingConfig = Field(
        default_factory=ReportingConfig,
        description="Report generation settings",
    )
