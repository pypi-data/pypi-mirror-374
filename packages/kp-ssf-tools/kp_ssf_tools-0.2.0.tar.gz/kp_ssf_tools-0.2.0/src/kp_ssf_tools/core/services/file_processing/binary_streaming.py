"""Binary content streaming protocols and implementations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from kp_ssf_tools.core.services.file_processing.interfaces import ContentStreamer

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path

    from .streaming import FileContentStreamer


class BinaryContentStreamer:
    """
    Binary content streamer for entropy analysis and raw data processing.

    Provides efficient streaming access to binary file content with configurable
    chunk sizes for entropy analysis, sliding window operations, and statistical
    analysis.
    """

    def __init__(self, file_path: Path, chunk_size: int = 4096) -> None:
        """
        Initialize the binary content streamer.

        Args:
            file_path: Path to the file to stream
            chunk_size: Default chunk size for streaming operations (default: 4KiB)

        """
        self.file_path = file_path
        self.chunk_size = chunk_size
        self._cached_header: bytes | None = None

    def get_file_header(self, bytes_count: int = 1024) -> bytes:
        """
        Get the first N bytes of the file with caching.

        Args:
            bytes_count: Number of bytes to retrieve from the beginning

        Returns:
            First bytes_count bytes of the file

        """
        if self._cached_header is None or len(self._cached_header) < bytes_count:
            with self.file_path.open("rb") as file:
                self._cached_header = file.read(bytes_count)

        return self._cached_header[:bytes_count]

    def stream_chunks(self, chunk_size: int | None = None) -> Generator[bytes]:
        """
        Stream the file in binary chunks.

        Args:
            chunk_size: Size of each chunk (uses instance default if None)

        Yields:
            Binary chunks of the specified size

        """
        effective_chunk_size = chunk_size or self.chunk_size

        with self.file_path.open("rb") as file:
            while chunk := file.read(effective_chunk_size):
                yield chunk

    def stream_sliding_window(
        self,
        window_size: int,
        step_size: int | None = None,
    ) -> Generator[tuple[int, bytes]]:
        """
        Stream overlapping windows of binary data for entropy analysis.

        Args:
            window_size: Size of each window in bytes
            step_size: Step size between windows (defaults to window_size for non-overlapping)

        Yields:
            Tuples of (offset, window_data) for each window

        """
        effective_step_size = step_size or window_size

        with self.file_path.open("rb") as file:
            # Read the entire file for sliding window analysis
            # For very large files, this could be optimized with buffering
            data = file.read()

        for offset in range(0, len(data) - window_size + 1, effective_step_size):
            window_data = data[offset : offset + window_size]
            yield offset, window_data

    def get_byte_range(self, start: int, length: int) -> bytes:
        """
        Get a specific range of bytes from the file.

        Args:
            start: Starting byte offset
            length: Number of bytes to read

        Returns:
            The requested byte range

        """
        with self.file_path.open("rb") as file:
            file.seek(start)
            return file.read(length)

    def get_file_size(self) -> int:
        """
        Get the total size of the file in bytes.

        Returns:
            File size in bytes

        """
        return self.file_path.stat().st_size

    def stream_entropy_blocks(
        self,
        block_size: int = 64,
        step_size: int = 16,
    ) -> Generator[tuple[int, bytes]]:
        """
        Stream blocks optimized for entropy analysis.

        Common entropy analysis uses 64-byte blocks with 16-byte steps
        for sliding window analysis.

        Args:
            block_size: Size of each entropy analysis block (default: 64 bytes)
            step_size: Step between blocks (default: 16 bytes)

        Yields:
            Tuples of (offset, block_data) for entropy calculation

        """
        yield from self.stream_sliding_window(block_size, step_size)

    def get_byte_frequencies(self, data: bytes | None = None) -> dict[int, int]:
        """
        Calculate byte frequency distribution for the entire file or given data.

        Args:
            data: Optional byte data to analyze (reads entire file if None)

        Returns:
            Dictionary mapping byte values (0-255) to their frequencies

        """
        if data is None:
            with self.file_path.open("rb") as file:
                data = file.read()

        frequencies = dict.fromkeys(range(256), 0)
        for byte in data:
            frequencies[byte] += 1

        return frequencies


class HybridContentStreamer(ContentStreamer):
    """
    Hybrid content streamer that can handle both text and binary operations.

    Extends the ContentStreamer protocol to provide both text-based operations
    (for backward compatibility) and binary operations (for entropy analysis).
    """

    def __init__(
        self,
        file_path: Path,
        encoding: str = "utf-8",
        chunk_size: int = 4096,
    ) -> None:
        """
        Initialize the hybrid content streamer.

        Args:
            file_path: Path to the file to stream
            encoding: Character encoding for text operations
            chunk_size: Default chunk size for binary operations

        """
        self.file_path = file_path
        self.encoding = encoding
        self.chunk_size = chunk_size
        self._text_streamer: FileContentStreamer | None = None
        self._binary_streamer: BinaryContentStreamer | None = None

    @property
    def text_streamer(self) -> FileContentStreamer:
        """Get or create the text content streamer."""
        if self._text_streamer is None:
            # Import here to avoid circular imports
            from .streaming import FileContentStreamer

            self._text_streamer = FileContentStreamer(self.file_path, self.encoding)
        return self._text_streamer

    @property
    def binary_streamer(self) -> BinaryContentStreamer:
        """Get or create the binary content streamer."""
        if self._binary_streamer is None:
            self._binary_streamer = BinaryContentStreamer(
                self.file_path,
                self.chunk_size,
            )
        return self._binary_streamer

    # ContentStreamer protocol implementation (delegates to text streamer)
    def get_file_header(self, lines: int = 10) -> list[str]:
        """Get the first N lines of the file as text."""
        return self.text_streamer.get_file_header(lines)

    def stream_pattern_matches(
        self,
        pattern: str,
        *,
        max_matches: int | None = None,
        ignore_case: bool = True,
    ) -> Generator[str]:
        """Stream lines matching a regex pattern."""
        return self.text_streamer.stream_pattern_matches(
            pattern,
            max_matches=max_matches,
            ignore_case=ignore_case,
        )

    def stream_section_content(
        self,
        start_pattern: str,
        end_pattern: str | None = None,
        *,
        include_markers: bool = False,
        ignore_case: bool = True,
    ) -> Generator[str]:
        """Stream content between start and end patterns."""
        return self.text_streamer.stream_section_content(
            start_pattern,
            end_pattern,
            include_markers=include_markers,
            ignore_case=ignore_case,
        )

    def stream_lines(self) -> Generator[str]:
        """Stream all lines in the file as text."""
        return self.text_streamer.stream_lines()

    def find_first_match(
        self,
        pattern: str,
        *,
        ignore_case: bool = True,
    ) -> str | None:
        """Find the first line matching a pattern."""
        return self.text_streamer.find_first_match(pattern, ignore_case=ignore_case)

    def search_multiple_patterns(
        self,
        patterns: dict[str, str],
        *,
        ignore_case: bool = True,
        early_termination: bool = True,
    ) -> dict[str, list[str]]:
        """Search for multiple patterns in a single file pass."""
        return self.text_streamer.search_multiple_patterns(
            patterns,
            ignore_case=ignore_case,
            early_termination=early_termination,
        )

    # Binary operations (delegate to binary streamer)
    def get_binary_header(self, bytes_count: int = 1024) -> bytes:
        """Get the first N bytes of the file."""
        return self.binary_streamer.get_file_header(bytes_count)

    def stream_binary_chunks(self, chunk_size: int | None = None) -> Generator[bytes]:
        """Stream the file in binary chunks."""
        return self.binary_streamer.stream_chunks(chunk_size)

    def stream_sliding_window(
        self,
        window_size: int,
        step_size: int | None = None,
    ) -> Generator[tuple[int, bytes]]:
        """Stream overlapping windows of binary data."""
        return self.binary_streamer.stream_sliding_window(window_size, step_size)

    def stream_entropy_blocks(
        self,
        block_size: int = 64,
        step_size: int = 16,
    ) -> Generator[tuple[int, bytes]]:
        """Stream blocks optimized for entropy analysis."""
        return self.binary_streamer.stream_entropy_blocks(block_size, step_size)

    def get_byte_frequencies(self, data: bytes | None = None) -> dict[int, int]:
        """Calculate byte frequency distribution."""
        return self.binary_streamer.get_byte_frequencies(data)

    def get_file_size(self) -> int:
        """Get the total size of the file in bytes."""
        return self.binary_streamer.get_file_size()
