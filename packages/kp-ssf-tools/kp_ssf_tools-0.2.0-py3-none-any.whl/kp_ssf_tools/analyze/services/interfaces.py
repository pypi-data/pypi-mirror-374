"""Interfaces and protocols for entropy analysis services."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, NamedTuple, Protocol, runtime_checkable

if TYPE_CHECKING:
    from pathlib import Path

    from kp_ssf_tools.analyze.models.analysis import (
        ComplianceReport,
        CredentialAnalysisResult,
        CryptoStructure,
        EntropyAnalysisResult,
        EntropyRegion,
        FileAnalysisResult,
        FileType,
        StatisticalTest,
    )
    from kp_ssf_tools.analyze.models.content_aware import ContentAwareThresholds
    from kp_ssf_tools.analyze.models.types import EntropyLevel


# File Classification and Type Detection
@runtime_checkable
class FileTypeClassifierProtocol(Protocol):
    """Protocol for file type detection and classification."""

    def classify_file(self, file_path: Path) -> tuple[FileType, str | None]:
        """
        Classify file type and detect programming language.

        Args:
            file_path: Path to the file to classify

        Returns:
            Tuple of (FileType, programming_language_or_None)

        """
        ...

    def load_file_content(self, file_path: Path) -> bytes:
        """
        Load file content for analysis.

        Args:
            file_path: Path to the file to load

        Returns:
            File content as bytes

        """
        ...


# Content-Aware Threshold Management
@runtime_checkable
class ThresholdProviderProtocol(Protocol):
    """Protocol for content-aware entropy threshold management."""

    def get_thresholds(self, file_type: FileType) -> ContentAwareThresholds:
        """
        Get entropy thresholds for specific file type.

        Args:
            file_type: The detected file type

        Returns:
            ContentAwareThresholds model with all threshold values

        """
        ...

    def classify_entropy_level(
        self,
        entropy: float,
        file_type: FileType,
    ) -> EntropyLevel:
        """
        Classify entropy level based on content-aware thresholds.

        Args:
            entropy: Shannon entropy value
            file_type: The detected file type

        Returns:
            Entropy level classification enum

        """
        ...


# Core Entropy Analysis
@runtime_checkable
class EntropyAnalyzerProtocol(Protocol):
    """Protocol for Shannon entropy calculation and analysis."""

    def calculate_entropy(self, data: bytes) -> float:
        """
        Calculate Shannon entropy for data.

        Args:
            data: Data to analyze

        Returns:
            Shannon entropy in bits per byte (0.0-8.0)

        """
        ...

    def analyze_sliding_window(
        self,
        data: bytes,
        window_size: int,
        step_size: int,
    ) -> list[EntropyRegion]:
        """
        Perform sliding window entropy analysis.

        Args:
            data: Data to analyze
            window_size: Size of analysis window in bytes
            step_size: Step size for sliding window

        Returns:
            List of entropy regions with analysis results

        """
        ...

    def analyze_file_entropy(
        self,
        file_path: Path,
        *,
        analysis_block_size: int,
        step_size: int,
        file_chunk_size: int,
        force_file_type: FileType | None = None,
    ) -> FileAnalysisResult:
        """
        Analyze entropy of a complete file.

        Args:
            file_path: Path to file to analyze
            analysis_block_size: Size of analysis blocks in bytes (from config)
            step_size: Step size for sliding window (from config)
            file_chunk_size: Size of file I/O chunks in bytes (from config)
            force_file_type: Override automatic file type detection

        Returns:
            Complete file analysis result

        """
        ...


# Detection Services
@runtime_checkable
class DetectorProtocol(Protocol):
    """Base protocol for structure detection services."""

    def detect(self, data: bytes, file_type: FileType) -> list[CryptoStructure]:
        """
        Detect structures in data.

        Args:
            data: Data to analyze
            file_type: Detected file type

        Returns:
            List of detected cryptographic structures

        """
        ...

    def get_supported_types(self) -> set[FileType]:
        """
        Get file types supported by this detector.

        Returns:
            Set of supported FileType values

        """
        ...


@runtime_checkable
class CryptoStructureDetectorProtocol(DetectorProtocol, Protocol):
    """Protocol for cryptographic structure detection."""

    def detect_sboxes(self, data: bytes) -> list[CryptoStructure]:
        """
        Detect S-box patterns in data.

        Args:
            data: Data to analyze

        Returns:
            List of detected S-box structures

        """
        ...

    def detect_round_constants(self, data: bytes) -> list[CryptoStructure]:
        """
        Detect cryptographic round constants.

        Args:
            data: Data to analyze

        Returns:
            List of detected round constant structures

        """
        ...

    def detect_base64_data(self, data: bytes) -> list[CryptoStructure]:
        """
        Detect Base64 encoded data blocks.

        Args:
            data: Data to analyze

        Returns:
            List of detected Base64 structures

        """
        ...


class CredentialScanOptions(NamedTuple):
    """Options for credential scanning operations."""

    scan_type: str = "comprehensive"  # comprehensive, quick, targeted
    severity_threshold: str = "medium"  # low, medium, high
    include_files: tuple[str, ...] = ()  # Glob patterns for inclusion
    exclude_files: tuple[str, ...] = ()  # Glob patterns for exclusion
    max_file_size: int = 100 * 1024 * 1024  # 100MB default
    confidence_threshold: float = 0.7  # Minimum confidence for reporting
    recursive: bool = True  # Whether to scan recursively
    file_extensions: tuple[str, ...] = ()  # File extensions to scan
    context_lines: int = 3  # Number of context lines around matches
    scan_binary_files: bool = False  # Whether to scan binary files
    max_binary_size_mb: int = 10  # Maximum binary file size in MB


@runtime_checkable
class CredentialDetectionProtocol(Protocol):
    """Protocol for credential detection services that scan for sensitive information."""

    def scan_file(
        self,
        file_path: Path,
        options: CredentialScanOptions | None = None,
    ) -> list[CryptoStructure]:
        """
        Scan a single file for credential patterns.

        Args:
            file_path: Path to file to scan
            options: Optional scanning configuration

        Returns:
            List of detected credential structures

        """
        ...

    def scan_directory(
        self,
        directory_path: Path,
        options: CredentialScanOptions | None = None,
    ) -> dict[Path, list[CryptoStructure]]:
        """
        Scan a directory recursively for credential patterns.

        Args:
            directory_path: Path to directory to scan
            options: Optional scanning configuration

        Returns:
            Dictionary mapping file paths to detected credentials

        """
        ...

    def analyze_files(
        self,
        target_paths: list[Path],
        config: dict[str, dict[str, object]],
        options: CredentialScanOptions | None = None,
    ) -> CredentialAnalysisResult:
        """
        Analyze files for credential patterns.

        Args:
            target_paths: List of paths to analyze
            config: Analysis configuration
            options: Optional scanning configuration

        Returns:
            Analysis result with detected credentials

        """
        ...

    def get_supported_patterns(self) -> list[str]:
        """
        Get list of supported credential patterns.

        Returns:
            List of pattern names/types this detector supports

        """
        ...


@runtime_checkable
class CredentialDetectorProtocol(DetectorProtocol, Protocol):
    """Protocol for credential and API key detection."""

    def detect_username_patterns(self, text: str) -> list[CryptoStructure]:
        """
        Detect username patterns in text.

        Args:
            text: Text content to analyze

        Returns:
            List of detected username patterns

        """
        ...

    def detect_password_patterns(self, text: str) -> list[CryptoStructure]:
        """
        Detect password patterns in text.

        Args:
            text: Text content to analyze

        Returns:
            List of detected password patterns

        """
        ...

    def detect_api_key_patterns(self, text: str) -> list[CryptoStructure]:
        """
        Detect API key patterns in text.

        Args:
            text: Text content to analyze

        Returns:
            List of detected API key patterns

        """
        ...


# Wordlist Management
@runtime_checkable
class WordlistManagerProtocol(Protocol):
    """Protocol for SecLists wordlist management and caching."""

    def ensure_wordlists_available(self, *, offline_mode: bool = False) -> bool:
        """
        Ensure wordlists are available, downloading if necessary.

        Args:
            offline_mode: If True, skip downloads and use cached data only

        Returns:
            True if wordlists are available, False otherwise

        """
        ...

    def get_usernames(self) -> set[str]:
        """
        Get username wordlist.

        Returns:
            Set of common usernames

        """
        ...

    def get_passwords(self) -> set[str]:
        """
        Get password wordlist.

        Returns:
            Set of common passwords

        """
        ...

    def has_cached_wordlists(self) -> bool:
        """
        Check if wordlists are cached locally.

        Returns:
            True if cached wordlists exist

        """
        ...


# Statistical Analysis
@runtime_checkable
class StatisticalTestRunnerProtocol(Protocol):
    """Protocol for statistical analysis of entropy data."""

    def run_normality_tests(self, entropy_values: list[float]) -> list[StatisticalTest]:
        """
        Run normality tests on entropy data.

        Args:
            entropy_values: List of entropy values to test

        Returns:
            List of statistical test results

        """
        ...

    def detect_outliers(
        self,
        entropy_values: list[float],
        confidence_level: float = 0.95,
    ) -> list[int]:
        """
        Detect outliers in entropy data.

        Args:
            entropy_values: List of entropy values
            confidence_level: Statistical confidence level

        Returns:
            List of indices of outlier values

        """
        ...

    def calculate_correlation(
        self,
        entropy_regions: list[EntropyRegion],
        crypto_structures: list[CryptoStructure],
    ) -> float:
        """
        Calculate correlation between entropy anomalies and crypto structures.

        Args:
            entropy_regions: List of entropy regions
            crypto_structures: List of detected crypto structures

        Returns:
            Correlation coefficient (-1.0 to 1.0)

        """
        ...


# Report Generation
@runtime_checkable
class FormatterProtocol(Protocol):
    """Protocol for output formatting services."""

    def format_analysis_result(self, result: EntropyAnalysisResult) -> str:
        """
        Format analysis result for output.

        Args:
            result: Complete entropy analysis result

        Returns:
            Formatted output string

        """
        ...

    def format_file_result(self, result: FileAnalysisResult) -> str:
        """
        Format single file analysis result.

        Args:
            result: File analysis result

        Returns:
            Formatted output string

        """
        ...


@runtime_checkable
class ComplianceReporterProtocol(Protocol):
    """Protocol for PCI SSF compliance reporting."""

    def generate_compliance_report(
        self,
        analysis_result: EntropyAnalysisResult,
        *,
        include_evidence: bool = True,
    ) -> ComplianceReport:
        """
        Generate PCI SSF 2.3 compliance report.

        Args:
            analysis_result: Complete entropy analysis result
            include_evidence: Whether to include detailed evidence

        Returns:
            Compliance report with findings and evidence

        """
        ...

    def assess_compliance_status(
        self,
        crypto_structures: list[CryptoStructure],
        entropy_regions: list[EntropyRegion],
    ) -> str:
        """
        Assess overall compliance status.

        Args:
            crypto_structures: Detected crypto structures
            entropy_regions: Entropy analysis regions

        Returns:
            Compliance status string

        """
        ...


# Text Processing Utilities
@runtime_checkable
class TextProcessorProtocol(Protocol):
    """Protocol for text processing operations used by detectors."""

    def find_pattern(
        self,
        pattern: str,
        text: str,
        flags: int = 0,
    ) -> list[tuple[int, int, str]]:
        """
        Find regex pattern matches in text.

        Args:
            pattern: Regular expression pattern
            text: Text to search
            flags: Regex flags

        Returns:
            List of (start_pos, end_pos, match_text) tuples

        """
        ...

    def decode_base64(self, data: str) -> bytes:
        """
        Decode base64 string.

        Args:
            data: Base64 encoded string

        Returns:
            Decoded bytes

        """
        ...

    def calculate_entropy(self, data: bytes | str) -> float:
        """
        Calculate Shannon entropy.

        Args:
            data: Data to analyze

        Returns:
            Shannon entropy value

        """
        ...


# Analysis Orchestration
@runtime_checkable
class AnalysisOrchestratorProtocol(Protocol):
    """Protocol for coordinating the overall entropy analysis workflow."""

    def analyze_target(
        self,
        target_path: Path,
        config: dict[str, object],
    ) -> EntropyAnalysisResult:
        """
        Orchestrate complete entropy analysis of a target.

        Args:
            target_path: Path to file or directory to analyze
            config: Analysis configuration parameters

        Returns:
            Complete analysis result

        """
        ...

    def analyze_single_file(
        self,
        file_path: Path,
        config: dict[str, object],
    ) -> FileAnalysisResult:
        """
        Analyze a single file.

        Args:
            file_path: Path to file to analyze
            config: Analysis configuration parameters

        Returns:
            Single file analysis result

        """
        ...


# Abstract Base Classes for Shared Implementation


class AbstractDetector(ABC):
    """Abstract base class for detectors with shared functionality."""

    def __init__(
        self,
        output_service: object,  # RichOutputProtocol
        config_service: object,  # ConfigurationServiceProtocol
        http_client: object | None = None,  # HttpClientProtocol | None
        timestamp_service: object | None = None,  # TimestampProtocol | None
    ) -> None:
        """Initialize detector with injected core services."""
        self.output = output_service
        self.config = config_service
        self.http_client = http_client
        self.timestamp = timestamp_service

    @abstractmethod
    def detect(self, data: bytes, file_type: FileType) -> list[CryptoStructure]:
        """Detect structures in data."""
        ...

    @abstractmethod
    def get_supported_types(self) -> set[FileType]:
        """Get supported file types."""
        ...


class AbstractFormatter(ABC):
    """Abstract base class for formatters with shared functionality."""

    def __init__(
        self,
        output_service: object,  # RichOutputProtocol
        timestamp_service: object | None = None,  # TimestampProtocol | None
    ) -> None:
        """Initialize formatter with injected services."""
        self.output = output_service
        self.timestamp = timestamp_service

    @abstractmethod
    def format_analysis_result(self, result: EntropyAnalysisResult) -> str:
        """Format complete analysis result."""
        ...

    def _sanitize_data_sample(self, data: bytes | str, max_length: int = 64) -> str:
        """Sanitize data samples for safe output."""
        if isinstance(data, bytes):
            # Convert bytes to hex representation for safety
            hex_data = data[:max_length].hex()
            return f"[{hex_data[:max_length]}{'...' if len(data) > max_length else ''}]"
        # Sanitize string data
        sanitized = data[:max_length].replace("\n", "\\n").replace("\r", "\\r")
        return f'"{sanitized}{"..." if len(data) > max_length else ""}"'

    def _format_confidence(self, confidence: float) -> str:
        """Format confidence score consistently."""
        return f"{confidence:.2%}"

    def _format_entropy(self, entropy: float) -> str:
        """Format entropy value consistently."""
        return f"{entropy:.3f}"
