"""Entropy analysis input and result models."""

from __future__ import annotations

from datetime import datetime  # noqa: TC003
from pathlib import Path  # noqa: TC003

from pydantic import Field

from kp_ssf_tools.analyze.models.types import (
    ComplianceStatus,
    CredentialRiskLevel,
    CryptoStructureType,
    EntropyLevel,
    FileType,
)
from kp_ssf_tools.models.base import SSFToolsBaseModel

# Export the imported types for external use
__all__ = [
    "BinaryLocationMixin",
    "ComplianceReport",
    "ComplianceStatus",
    "CredentialAnalysisResult",
    "CredentialLocationMixin",
    "CredentialPattern",
    "CredentialRiskLevel",
    "CryptoStructure",
    "CryptoStructureType",
    "DetectedCredential",
    "EntropyAnalysisResult",
    "EntropyInputModel",
    "EntropyLevel",
    "EntropyRegion",
    "EvidenceItem",
    "FileAnalysisResult",
    "FileType",
    "StatisticalTest",
    "TextCryptoStructure",
    "TextEntropyRegion",
    "TextLocationMixin",
]


class EntropyInputModel(SSFToolsBaseModel):
    """
    User inputs for entropy analysis - PCI SSF 2.3 compliance focused.

    This model is designed to work with dependency injection containers
    and can be populated from CLI arguments or configuration files.
    """

    target_path: Path  # File or directory to analyze
    output_file: Path | None = None  # Output file path
    block_size: int = Field(
        default=64,
        gt=0,
        description="Analysis block size in bytes",
    )
    window_step: int = Field(default=16, gt=0, description="Sliding window step size")
    force_file_type: FileType | None = None  # Override file type detection
    recursive: bool = True  # Recursive directory analysis (default)
    file_types: list[str] | None = None  # File type filters
    include_statistical: bool = True  # Include statistical tests
    detect_crypto: bool = True  # Enable crypto structure detection
    use_seclists: bool = True  # Enable SecLists wordlist downloading
    refresh_cache: bool = False  # Force refresh of SecLists cache
    offline_mode: bool = False  # Disable all network operations


# Base Location Models


class BinaryLocationMixin(SSFToolsBaseModel):
    """Base class for binary file location information."""

    offset: int = Field(ge=0, description="Byte offset in file")
    size: int = Field(gt=0, description="Region/structure size in bytes")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")


class TextLocationMixin(BinaryLocationMixin):
    """Extended location information for text-based files."""

    line_start: int | None = None  # Starting line number (1-based, for text files)
    line_end: int | None = None  # Ending line number (1-based, for text files)
    column_start: int | None = None  # Starting column (1-based, for text files)
    column_end: int | None = None  # Ending column (1-based, for text files)


# Analysis Result Models


class EntropyRegion(BinaryLocationMixin):
    """Represents a region with specific entropy characteristics in binary files."""

    entropy: float  # Shannon entropy (bits/byte)
    level: EntropyLevel  # Classification level
    data_sample: bytes  # Sample of the data (first 32 bytes)

    # Statistical analysis integration fields
    statistical_significance: str | None = None  # Statistical test significance marker
    modification_reason: str | None = None  # Reason for classification changes


class TextEntropyRegion(TextLocationMixin):
    """Represents a region with specific entropy characteristics in text files."""

    entropy: float  # Shannon entropy (bits/byte)
    level: EntropyLevel  # Classification level
    data_sample: str  # Sample of the text content

    # Statistical analysis integration fields
    statistical_significance: str | None = None  # Statistical test significance marker
    modification_reason: str | None = None  # Reason for classification changes


class CryptoStructure(BinaryLocationMixin):
    """Detected cryptographic structure in binary files."""

    structure_type: CryptoStructureType
    entropy: float  # Entropy of this structure
    description: str  # Human-readable description
    related_algorithms: list[str]  # Associated crypto algorithms


class TextCryptoStructure(TextLocationMixin):
    """Detected cryptographic structure in text files (e.g., embedded keys, base64)."""

    structure_type: CryptoStructureType
    entropy: float  # Entropy of this structure
    description: str  # Human-readable description
    related_algorithms: list[str]  # Associated crypto algorithms
    raw_text: str  # The actual text content detected


class StatisticalTest(SSFToolsBaseModel):
    """Statistical test result."""

    test_name: str
    test_value: float
    p_value: float | None
    passed: bool
    description: str


# Compliance Models


class EvidenceItem(SSFToolsBaseModel):
    """Audit trail evidence item for compliance reporting."""

    confidence: float  # Detection confidence (0.0-1.0)
    detection_method: str  # Method used for detection
    risk_level: str  # HIGH, MEDIUM, LOW
    description: str  # Human-readable description
    raw_data_sample: str  # Sample of detected data (sanitized)


class ComplianceReport(SSFToolsBaseModel):
    """PCI SSF 2.3 specific compliance report."""

    summary: str  # Executive summary
    status: ComplianceStatus
    evidence_items: list[EvidenceItem] = Field(default_factory=list)
    generation_timestamp: datetime
    tool_version: str


# Complete Analysis Results


class FileAnalysisResult(SSFToolsBaseModel):
    """Complete analysis result for a single file."""

    file_path: Path
    file_size: int
    file_type: FileType
    detected_language: str | None
    overall_entropy: float
    entropy_regions: list[EntropyRegion | TextEntropyRegion]
    crypto_structures: list[CryptoStructure | TextCryptoStructure]
    statistical_tests: list[StatisticalTest]
    anomaly_score: float  # Overall risk score (0.0-10.0)
    analysis_duration: float  # Analysis time in seconds


class EntropyAnalysisResult(SSFToolsBaseModel):
    """Complete analysis results for all processed files."""

    # Schema versioning and metadata
    schema_version: str = "1.0.0"  # Schema format version
    tool_version: str  # SSF-Tools version that generated this result
    generation_timestamp: datetime  # When the analysis was performed
    commit_hash: str | None = None  # Git commit hash if available

    # Analysis configuration and results
    input_config: EntropyInputModel
    files_analyzed: int
    total_size: int
    analysis_start: datetime
    analysis_end: datetime
    file_results: list[FileAnalysisResult]
    summary_statistics: dict[str, float]
    high_risk_findings: list[FileAnalysisResult]


# Additional analysis result models would go here
# (FileAnalysisResult, EntropyAnalysisResult, etc.)


# Credential Detection Models


class CredentialLocationMixin(TextLocationMixin):
    """Location information for detected credentials in text files."""

    context_before: str = Field(default="", description="Content before the match")
    context_after: str = Field(default="", description="Content after the match")
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Detection confidence (0.0-1.0)",
    )


class DetectedCredential(CredentialLocationMixin):
    """Base class for detected credentials in text files."""

    pattern_type: str = Field(
        ...,
        description="Type of credential pattern detected (detect-secrets detector type)",
    )
    risk_level: CredentialRiskLevel = Field(
        ...,
        description="Risk level of the detected credential",
    )
    value: str = Field(..., description="The detected credential value")
    detection_method: str = Field(
        ...,
        description="Method used for detection (regex, wordlist, etc.)",
    )

    @property
    def display_value(self) -> str:
        """Return a safe display version of the credential value."""
        credential_value_truncate_length = 50
        if len(self.value) > credential_value_truncate_length:
            return f"{self.value[:credential_value_truncate_length]}..."
        return self.value


class CredentialPattern(DetectedCredential):
    """A pattern detected by credential analysis."""

    # File path where this pattern was detected
    file_path: Path = Field(..., description="Path to file where pattern was detected")

    # Additional fields specific to pattern-based detection
    regex_pattern: str | None = Field(
        default=None,
        description="Regex pattern used for detection",
    )
    wordlist_source: str | None = Field(
        default=None,
        description="Source wordlist used for detection",
    )


class CredentialAnalysisResult(SSFToolsBaseModel):
    """Result from credential analysis containing all detected patterns."""

    file_path: Path = Field(..., description="Primary file path analyzed")
    patterns: list[CredentialPattern] = Field(
        default_factory=list,
        description="List of detected credential patterns",
    )
    total_patterns: int = Field(default=0, description="Total number of patterns found")
    processed_files: list[Path] = Field(
        default_factory=list,
        description="List of all files that were processed during analysis",
    )
    analysis_metadata: dict[str, str] = Field(
        default_factory=dict,
        description="Additional metadata about the analysis",
    )
