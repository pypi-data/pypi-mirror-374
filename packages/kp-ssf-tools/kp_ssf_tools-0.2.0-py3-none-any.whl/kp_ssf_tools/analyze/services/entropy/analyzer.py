"""
Shannon entropy analyzer with chunk-based processing and dependency injection.

This module implements normalized Shannon entropy calculation following the
implementation plan outlined in implementation-phases-and-deployment.md.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

from kp_ssf_tools.analyze.models.analysis import EntropyRegion
from kp_ssf_tools.analyze.models.types import EntropyLevel, FileType
from kp_ssf_tools.core.services.file_processing.interfaces import FileValidator
from kp_ssf_tools.core.services.rich_output.interfaces import RichOutputProtocol
from kp_ssf_tools.core.services.timestamp.interfaces import TimestampProtocol

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path

    from kp_ssf_tools.analyze.services.interfaces import ThresholdProviderProtocol
    from kp_ssf_tools.core.services.file_processing import (
        BinaryStreamerProtocol,
        FileProcessingService,
        FileValidator,
        MimeTypeDetector,
    )
    from kp_ssf_tools.core.services.rich_output.interfaces import RichOutputProtocol
    from kp_ssf_tools.core.services.timestamp.interfaces import TimestampProtocol


@dataclass
class SlidingWindowParams:
    """Parameters for sliding window processing."""

    analysis_block_size: int
    step_size: int
    file_type: FileType
    total_bytes: int
    current_region_count: int


@dataclass
class AnalysisYield:
    """Single yield from analysis generator."""

    type: str  # 'region' or 'summary'
    data: dict


class EntropyAnalyzer:
    """
    Shannon entropy analyzer with content-aware thresholds and chunk processing.

    Implements normalized Shannon entropy calculation with file-type-specific
    thresholds for PCI SSF 2.3 compliance detection. Uses dependency injection
    for core services and file processing capabilities.
    """

    def __init__(  # noqa: PLR0913
        self,
        rich_output: RichOutputProtocol,
        timestamp_service: TimestampProtocol,
        file_validator: FileValidator,
        mime_detector: MimeTypeDetector,
        file_processing: FileProcessingService,
        threshold_manager: ThresholdProviderProtocol,
    ) -> None:
        """
        Initialize entropy analyzer with injected core services.

        Args:
            rich_output: Rich output service for progress reporting and results display
            timestamp_service: Timestamp service for analysis timing
            file_validator: File validation service
            mime_detector: MIME type detection service for file classification
            file_processing: Service for file processing operations
            threshold_manager: Content-aware threshold management service

        """
        self.rich_output: RichOutputProtocol = rich_output
        self.timestamp: TimestampProtocol = timestamp_service
        self.file_validator: FileValidator = file_validator
        self.mime_detector: MimeTypeDetector = mime_detector
        self.file_processing: FileProcessingService = file_processing
        self.threshold_manager: ThresholdProviderProtocol = threshold_manager

    def calculate_shannon_entropy(self, data: bytes) -> float:
        """
        Calculate Shannon entropy for binary data in bits per byte.

        Uses the standard Shannon entropy formula: H(X) = -sum(p(x) * log2(p(x)))
        where p(x) is the probability of byte value x.

        Args:
            data: Binary data to analyze

        Returns:
            Shannon entropy in bits per byte (0.0 to 8.0, where 8.0 is maximum entropy)

        Raises:
            ValueError: If data is empty

        Note:
            - Maximum entropy (8.0): All 256 byte values occur with equal probability
            - Minimum entropy (0.0): Only one byte value occurs
            - Result range [0, 8] matches research-based thresholds in configuration

        """
        if not data:
            msg = "Cannot calculate entropy for empty data"
            raise ValueError(msg)

        # Calculate byte frequency distribution
        byte_counts = [0] * 256
        for byte in data:
            byte_counts[byte] += 1

        # Calculate probabilities and entropy
        data_length = len(data)
        entropy = 0.0

        for count in byte_counts:
            if count > 0:
                probability = count / data_length
                entropy -= probability * math.log2(probability)

        # Return raw entropy in bits per byte (0.0 to 8.0 range)
        return entropy

    def analyze_file_generator(  # noqa: PLR0913
        self,
        file_path: Path,
        *,
        min_risk_level: EntropyLevel = EntropyLevel.MEDIUM_HIGH,
        file_chunk_size: int = 65536,
        analysis_block_size: int = 64,
        step_size: int = 16,
        force_file_type: FileType | None = None,
        include_samples: bool = False,
    ) -> Generator[AnalysisYield]:
        """
        Generate analysis results as they're computed.

        Yields high-risk regions immediately, summary at end.

        Memory efficient streaming analysis - only creates objects for regions
        that meet the risk threshold criteria.

        Args:
            file_path: Path to file to analyze
            min_risk_level: Minimum risk level to yield regions
            file_chunk_size: Size of file I/O chunks in bytes
            analysis_block_size: Size of analysis blocks in bytes
            step_size: Step size for sliding window
            force_file_type: Override automatic file type detection
            include_samples: Whether to include data samples in regions

        Yields:
            AnalysisYield objects containing either:
            - High-risk region data (type='region')
            - Final summary statistics (type='summary')

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is empty or unreadable

        """
        # Defensive conversion: ensure min_risk_level is always EntropyLevel
        if isinstance(min_risk_level, str):
            min_risk_level = EntropyLevel(min_risk_level)

        # Record start time for per-file processing duration
        start_time = self.timestamp.now()

        # Validate file exists and is accessible
        if not self.file_validator.validate_file_exists(file_path):
            msg = f"File not found or not accessible: {file_path}"
            raise FileNotFoundError(msg)

        # Detect file type for content-aware analysis
        file_type = force_file_type or self._detect_file_type(file_path)
        self.rich_output.debug(f"Detected file type: {file_type.value}")

        # Create binary streamer for chunk-based processing
        binary_streamer: BinaryStreamerProtocol = (
            self.file_processing.create_binary_streamer(
                file_path,
                chunk_size=file_chunk_size,
            )
        )

        # Check if file is empty
        file_size = binary_streamer.get_file_size()
        if file_size == 0:
            msg = f"Cannot analyze empty file: {file_path}"
            raise ValueError(msg)

        # Initialize counters and state
        global_byte_counts = [0] * 256
        total_bytes = 0
        total_regions = 0
        high_risk_regions = 0
        overlap_buffer = b""
        current_offset = 0

        self.rich_output.debug(
            f"Streaming analysis with threshold {min_risk_level.value}: "
            f"{file_chunk_size}-byte chunks, {analysis_block_size}-byte blocks",
        )

        try:
            # Single-pass file processing with streaming output
            for chunk in binary_streamer.stream_chunks():
                # Update global byte frequency distribution
                for byte in chunk:
                    global_byte_counts[byte] += 1
                    total_bytes += 1

                # Process sliding windows within this chunk
                processing_data = overlap_buffer + chunk
                processing_offset = current_offset - len(overlap_buffer)

                pos = 0
                while pos + analysis_block_size <= len(processing_data):
                    # Extract analysis block
                    block_data = processing_data[pos : pos + analysis_block_size]
                    block_offset = processing_offset + pos

                    # Calculate entropy
                    block_entropy = self.calculate_shannon_entropy(block_data)
                    entropy_level = self._classify_entropy_level(
                        block_entropy,
                        file_type,
                    )
                    total_regions += 1

                    # Only create and yield region if it meets risk threshold
                    if entropy_level.order >= min_risk_level.order:
                        high_risk_regions += 1

                        # Prepare region data for streaming
                        region_data = {
                            "offset": block_offset,
                            "size": len(block_data),
                            "entropy": block_entropy,
                            "level": entropy_level.value,
                            "confidence": self._calculate_confidence(
                                block_entropy,
                                file_type,
                            ),
                        }

                        # Optionally include data sample
                        # Include "step_size + (analysis_block_size // 2)" bytes
                        if include_samples:
                            sample_size = step_size + (analysis_block_size // 2)
                            region_data["data_sample"] = block_data[:sample_size]

                        # Yield immediately - no accumulation
                        yield AnalysisYield(type="region", data=region_data)

                    # Move to next sliding window position
                    pos += step_size

                # Prepare overlap buffer for next chunk
                overlap_buffer = (
                    processing_data[-analysis_block_size:]
                    if len(processing_data) >= analysis_block_size
                    else processing_data
                )
                current_offset += len(chunk)

        except Exception as e:
            self.rich_output.error(f"Error during streaming entropy analysis: {e}")
            raise

        # Calculate overall file entropy from global distribution
        overall_entropy = self._calculate_file_entropy_from_distribution(
            global_byte_counts,
            total_bytes,
        )

        # Yield final summary
        # Detect MIME type and language for summary output
        mime_type = self.get_file_mime_type(file_path) or ""
        language = self.get_file_language(file_path) or ""
        # Calculate per-file processing time
        processing_time = (self.timestamp.now() - start_time).total_seconds()
        yield AnalysisYield(
            type="summary",
            data={
                "overall_entropy": overall_entropy,
                "total_regions": total_regions,
                "high_risk_regions": high_risk_regions,
                "file_size": file_size,
                "min_risk_level": min_risk_level.value,
                "mime_type": mime_type,
                "language": language,
                "processing_time": processing_time,
            },
        )

    def analyze_file_entropy(  # noqa: PLR0913
        self,
        file_path: Path,
        *,
        analysis_block_size: int,
        step_size: int,
        file_chunk_size: int,
        force_file_type: FileType | None = None,
        progress_callback: object | None = None,
    ) -> tuple[float, list[EntropyRegion]]:
        """
        Analyze entropy of a complete file using sliding window approach.

        Args:
            file_path: Path to file to analyze
            analysis_block_size: Size of analysis blocks in bytes (from config)
            step_size: Step size for sliding window (from config)
            file_chunk_size: Size of file I/O chunks in bytes (from config)
            force_file_type: Override automatic file type detection
            progress_callback: Optional callback for progress updates (progress, task_id)

        Returns:
            Tuple of (overall_entropy, entropy_regions)

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is empty or unreadable

        """
        # Validate file exists and is accessible
        if not self.file_validator.validate_file_exists(file_path):
            msg = f"File not found or not accessible: {file_path}"
            raise FileNotFoundError(msg)

        start_time = self.timestamp.now()

        # Detect file type for content-aware analysis
        file_type = force_file_type or self._detect_file_type(file_path)
        self.rich_output.debug(f"Detected file type: {file_type.value}")

        # Create binary streamer for chunk-based processing
        binary_streamer: BinaryStreamerProtocol = (
            self.file_processing.create_binary_streamer(
                file_path,
                chunk_size=file_chunk_size,
            )
        )

        # Check if file is empty
        file_size = binary_streamer.get_file_size()
        if file_size == 0:
            msg = f"Cannot analyze empty file: {file_path}"
            raise ValueError(msg)

        # Single-pass analysis: build global byte distribution and process sliding windows
        entropy_regions: list[EntropyRegion] = []
        # Global frequency distribution for true file entropy
        global_byte_counts = [0] * 256
        total_bytes = 0
        region_count = 0
        overlap_buffer = b""
        bytes_processed = 0

        self.rich_output.debug(
            f"Processing file in {file_chunk_size}-byte chunks with {analysis_block_size}-byte analysis blocks",
        )

        try:
            # Single-pass file processing
            for chunk in binary_streamer.stream_chunks():
                # Update global byte frequency distribution
                for byte in chunk:
                    global_byte_counts[byte] += 1
                    total_bytes += 1

                # Update progress
                bytes_processed += len(chunk)
                if progress_callback and callable(progress_callback):
                    progress_callback(bytes_processed, file_size)

                # Process sliding windows within this chunk
                params = SlidingWindowParams(
                    analysis_block_size=analysis_block_size,
                    step_size=step_size,
                    file_type=file_type,
                    total_bytes=total_bytes,
                    current_region_count=region_count,
                )
                regions, region_count, overlap_buffer = (
                    self._process_chunk_sliding_windows(
                        chunk=chunk,
                        overlap_buffer=overlap_buffer,
                        params=params,
                    )
                )
                entropy_regions.extend(regions)

        except Exception as e:
            self.rich_output.error(f"Error during entropy analysis: {e}")
            raise

        # Calculate true file entropy from global byte distribution
        overall_entropy = self._calculate_file_entropy_from_distribution(
            global_byte_counts,
            total_bytes,
        )

        end_time = self.timestamp.now()
        analysis_duration = (end_time - start_time).total_seconds()

        self.rich_output.debug(
            f"Entropy analysis complete in {analysis_duration:.2f}s",
        )

        return overall_entropy, entropy_regions

    def analyze_data_chunk(self, data: bytes, file_type: FileType) -> EntropyRegion:
        """
        Analyze entropy of a single data chunk.

        Args:
            data: Binary data chunk to analyze
            file_type: File type for content-aware classification

        Returns:
            EntropyRegion with analysis results

        """
        entropy = self.calculate_shannon_entropy(data)
        level = self._classify_entropy_level(entropy, file_type)
        confidence = self._calculate_confidence(entropy, file_type)

        return EntropyRegion(
            offset=0,  # Offset would be set by caller
            size=len(data),
            confidence=confidence,
            entropy=entropy,
            level=level,
            data_sample=data[:32],  # First 32 bytes for output
        )

    def get_entropy_threshold(self, file_type: FileType, level: EntropyLevel) -> float:
        """
        Get entropy threshold for a specific file type and level.

        Args:
            file_type: Type of file being analyzed
            level: Entropy level to get threshold for

        Returns:
            Entropy threshold value (0.0 to 1.0)

        """
        thresholds = self.threshold_manager.get_thresholds(file_type)

        # Map EntropyLevel to specific threshold attributes
        level_mapping = {
            EntropyLevel.VERY_LOW: thresholds.very_low_threshold,
            EntropyLevel.LOW: thresholds.low_threshold,
            EntropyLevel.MEDIUM: thresholds.medium_threshold,
            EntropyLevel.MEDIUM_HIGH: thresholds.medium_high_threshold,
            EntropyLevel.HIGH: thresholds.high_threshold,
            EntropyLevel.CRITICAL: 8.0,  # Above max entropy
        }

        return level_mapping.get(level, thresholds.medium_threshold)

    def _detect_file_type(self, file_path: Path) -> FileType:
        """
        Detect file type using MIME detection service.

        Args:
            file_path: Path to file to classify

        Returns:
            Detected FileType

        """
        try:
            mime_type = self.mime_detector.detect_mime_type(file_path)

            if mime_type is None:
                return FileType.UNKNOWN

            # Create mapping for better maintainability
            if mime_type.startswith("text/"):
                return self._classify_text_type(mime_type)
            if mime_type.startswith("application/"):
                return self._classify_application_type(mime_type)
            if mime_type.startswith(("image/", "video/")):
                return FileType.UNKNOWN  # Binary files mapped to UNKNOWN

        except OSError:
            self.rich_output.warning(
                f"Failed to detect file type for {file_path}, using UNKNOWN",
            )

        return FileType.UNKNOWN

    def _classify_text_type(self, mime_type: str) -> FileType:
        """Classify text MIME types."""
        # Map MIME types to specific programming languages
        language_mapping = {
            "python": FileType.PYTHON,
            "javascript": FileType.JAVASCRIPT,
            "java": FileType.JAVA,
            "c++": FileType.CPP,
        }

        for lang, file_type in language_mapping.items():
            if lang in mime_type:
                return file_type

        # Map text MIME types that are definitely documentation
        doc_mime_patterns = {
            "markdown",
            "plain",
            "csv",
            "html",
            "xml",
            "yaml",
            "json",
            "toml",
        }

        mime_lower = mime_type.lower()
        for pattern in doc_mime_patterns:
            if pattern in mime_lower:
                return FileType.DOCUMENTATION

        # For truly unknown text MIME types, return UNKNOWN instead of defaulting to DOCUMENTATION
        return FileType.UNKNOWN

    def _classify_application_type(self, mime_type: str) -> FileType:
        """Classify application MIME types."""
        # Map specific MIME type patterns to file types
        type_mapping = {
            "x-msdos": FileType.WINDOWS_PE,
            "x-msdownload": FileType.WINDOWS_PE,
            "x-sharedlib": FileType.LINUX_ELF,
            "x-object": FileType.LINUX_ELF,
            "x-mach-binary": FileType.MACOS_MACHO,
            "encrypted": FileType.ENCRYPTED,
            "pgp": FileType.ENCRYPTED,
        }

        for pattern, file_type in type_mapping.items():
            if pattern in mime_type:
                return file_type

        return FileType.UNKNOWN

    def _classify_entropy_level(
        self,
        entropy: float,
        file_type: FileType,
    ) -> EntropyLevel:
        """
        Classify entropy level using content-aware thresholds.

        Args:
            entropy: Calculated entropy value (0.0 to 8.0 bits per byte)
            file_type: Type of file for threshold selection

        Returns:
            EntropyLevel classification

        """
        return self.threshold_manager.classify_entropy_level(entropy, file_type)

    def _calculate_confidence(self, entropy: float, file_type: FileType) -> float:
        """
        Calculate confidence score for entropy classification.

        Args:
            entropy: Calculated entropy value
            file_type: File type for context

        Returns:
            Confidence score (0.0 to 1.0)

        """
        thresholds = self.threshold_manager.get_thresholds(file_type)

        # Calculate distance from expected range for this file type
        expected_range = (
            thresholds.low_threshold,
            thresholds.medium_high_threshold,
        )
        expected_center = (expected_range[0] + expected_range[1]) / 2

        # Distance from expected center, normalized
        distance = abs(entropy - expected_center)
        max_distance = max(
            abs(expected_range[0] - expected_center),
            abs(expected_range[1] - expected_center),
        )

        # Higher confidence for values further from expected range
        confidence = (
            min(1.0, distance / max_distance) if max_distance > 0 else 0.5
        )  # Moderate confidence for edge case

        return confidence

    def _process_chunk_sliding_windows(
        self,
        chunk: bytes,
        overlap_buffer: bytes,
        params: SlidingWindowParams,
    ) -> tuple[list[EntropyRegion], int, bytes]:
        """
        Process sliding windows within a chunk for entropy region detection.

        Args:
            chunk: Current data chunk from file
            overlap_buffer: Buffer from previous chunk to handle boundary windows
            params: Sliding window processing parameters

        Returns:
            Tuple of (entropy_regions, updated_region_count, new_overlap_buffer)

        """
        regions: list[EntropyRegion] = []
        region_count = params.current_region_count

        # Combine with overlap buffer from previous chunk
        processing_data = overlap_buffer + chunk
        processing_offset = params.total_bytes - len(processing_data)

        # Process sliding windows within this chunk
        current_pos = 0
        while current_pos + params.analysis_block_size <= len(processing_data):
            # Extract analysis block
            block_data = processing_data[
                current_pos : current_pos + params.analysis_block_size
            ]
            block_offset = processing_offset + current_pos

            # Calculate entropy for this block
            block_entropy = self.calculate_shannon_entropy(block_data)
            region_count += 1

            # Classify entropy level using content-aware thresholds
            entropy_level = self._classify_entropy_level(
                block_entropy,
                params.file_type,
            )

            # Create entropy region (limit data sample to first 32 bytes for output)
            region = EntropyRegion(
                offset=block_offset,
                size=len(block_data),
                confidence=self._calculate_confidence(block_entropy, params.file_type),
                entropy=block_entropy,
                level=entropy_level,
                data_sample=block_data[:32],  # Limit sample size for output
            )

            regions.append(region)

            # Move to next sliding window position
            current_pos += params.step_size

            # Progress reporting for large files
            if region_count % 1000 == 0:
                self.rich_output.debug(
                    f"Processed {region_count} regions (offset: {block_offset})",
                )

        # Prepare overlap buffer for next chunk (last analysis_block_size bytes)
        new_overlap_buffer = (
            processing_data[-params.analysis_block_size :]
            if len(processing_data) >= params.analysis_block_size
            else processing_data
        )

        return regions, region_count, new_overlap_buffer

    def _calculate_file_entropy_from_distribution(
        self,
        byte_counts: list[int],
        total_bytes: int,
    ) -> float:
        """
        Calculate Shannon entropy from global byte frequency distribution.

        Args:
            byte_counts: Array of byte frequency counts (length 256)
            total_bytes: Total number of bytes processed

        Returns:
            Shannon entropy in bits per byte (0.0 to 8.0)

        """
        if total_bytes == 0:
            return 0.0

        entropy = 0.0
        for count in byte_counts:
            if count > 0:
                probability = count / total_bytes
                entropy -= probability * math.log2(probability)

        return entropy

    def get_file_mime_type(self, file_path: Path) -> str | None:
        """
        Get MIME type for a file.

        Args:
            file_path: Path to file

        Returns:
            MIME type string or None if detection fails

        """
        return self.file_processing.detect_mime_type(file_path)

    def get_file_language(self, file_path: Path) -> str | None:
        """
        Get detected programming language for a file.

        Args:
            file_path: Path to file

        Returns:
            Language name string or None if detection fails

        """
        return self.file_processing.detect_language(file_path)
