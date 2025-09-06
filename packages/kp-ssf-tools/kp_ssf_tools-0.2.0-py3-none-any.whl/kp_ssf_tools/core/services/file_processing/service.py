"""Main file processing service implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from kp_ssf_tools.core.services.file_processing.interfaces import (
        BinaryStreamerProtocol,
        ContentStreamer,
        EncodingDetector,
        FileDiscoverer,
        FileValidator,
        HashGenerator,
        MimeTypeDetector,
    )
    from kp_ssf_tools.core.services.file_processing.language_detection import (
        PygmentsLanguageDetector,
    )
    from kp_ssf_tools.core.services.rich_output.interfaces import RichOutputProtocol
    from kp_ssf_tools.models.types import PathLike


class FileProcessingService:
    """Service for all file processing operations."""

    def __init__(  # noqa: PLR0913
        self,
        encoding_detector: EncodingDetector,
        hash_generator: HashGenerator,
        file_validator: FileValidator,
        file_discovery: FileDiscoverer,
        mime_detector: MimeTypeDetector,
        language_detector: PygmentsLanguageDetector,
        rich_output: RichOutputProtocol,
    ) -> None:
        """
        Initialize the file processing service.

        Args:
            encoding_detector: Service for detecting file encodings
            hash_generator: Service for generating file hashes
            file_validator: Service for validating file paths
            file_discovery: Service for finding files
            mime_detector: Service for detecting MIME types
            language_detector: Service for detecting programming languages
            rich_output: Service for rich console output

        """
        self.encoding_detector: EncodingDetector = encoding_detector
        self.hash_generator: HashGenerator = hash_generator
        self.file_validator: FileValidator = file_validator
        self.file_discovery: FileDiscoverer = file_discovery
        self.mime_detector: MimeTypeDetector = mime_detector
        self.language_detector: PygmentsLanguageDetector = language_detector
        self.rich_output: RichOutputProtocol = rich_output

    def process_file(self, file_path: Path) -> dict[str, str | bool | None]:
        """
        Process a file and return metadata.

        Args:
            file_path: Path to the file to process

        Returns:
            Dictionary containing file metadata including encoding, hash, path,
            MIME type, and text/binary classification.
            Returns empty dict if file validation fails.

        """
        if not self.file_validator.validate_file_exists(file_path):
            self.rich_output.error(f"File not found: {file_path}")
            return {}

        encoding: str | None = self.encoding_detector.detect_encoding(file_path)
        if encoding is None:
            self.rich_output.warning(f"Could not detect encoding for: {file_path}")
            return {}

        file_hash: str = self.hash_generator.generate_hash(file_path)

        # Get MIME type information
        mime_type: str | None = self.mime_detector.detect_mime_type(file_path)
        is_text: bool = self.mime_detector.is_text_file(file_path)

        return {
            "encoding": encoding,
            "hash": file_hash,
            "path": str(file_path),
            "mime_type": mime_type,
            "is_text": is_text,
        }

    def detect_encoding(self, file_path: Path) -> str | None:
        """
        Detect the encoding of a file.

        Args:
            file_path: Path to the file to analyze

        Returns:
            The detected encoding name, or None if detection fails

        """
        return self.encoding_detector.detect_encoding(file_path)

    def generate_hash(self, file_path: Path) -> str:
        """
        Generate hash for a file.

        Args:
            file_path: Path to the file to hash

        Returns:
            The generated hash as a hexadecimal string

        """
        return self.hash_generator.generate_hash(file_path)

    def detect_mime_type(self, file_path: Path) -> str | None:
        """
        Detect the MIME type of a file.

        Args:
            file_path: Path to the file to analyze

        Returns:
            The detected MIME type string, or None if detection fails

        """
        return self.mime_detector.detect_mime_type(file_path)

    def detect_language(self, file_path: Path) -> str | None:
        """
        Detect the programming language of a file using Pygments.

        Args:
            file_path: Path to the file to analyze

        Returns:
            The detected language name string, or None if detection fails

        """
        from kp_ssf_tools.analyze.models.types import FileType

        file_type = self.language_detector.detect_language(file_path)
        return file_type.value if file_type != FileType.UNKNOWN else None

    def is_text_file(self, file_path: Path) -> bool:
        """
        Check if a file is a text file based on its MIME type.

        Args:
            file_path: Path to the file to check

        Returns:
            True if the file is detected as a text file, False otherwise

        """
        return self.mime_detector.is_text_file(file_path)

    def is_binary_file(self, file_path: Path) -> bool:
        """
        Check if a file is a binary file based on its MIME type.

        Args:
            file_path: Path to the file to check

        Returns:
            True if the file is detected as a binary file, False otherwise

        """
        return self.mime_detector.is_binary_file(file_path)

    def discover_files_by_pattern(
        self,
        base_path: PathLike,
        pattern: str = "*",
        *,
        recursive: bool = False,
    ) -> list[Path]:
        """
        Discover files matching a pattern in a directory.

        Args:
            base_path: Directory to search for files
            pattern: Glob pattern to match files (default: "*")
            recursive: If True, search subdirectories recursively (default: False)

        Returns:
            List of Path objects for all matching files

        """
        return self.file_discovery.discover_files_by_pattern(
            base_path,
            pattern,
            recursive=recursive,
        )

    def create_content_streamer(
        self,
        file_path: Path,
        encoding: str | None = None,
    ) -> ContentStreamer:
        """
        Create a content streamer for efficient file reading.

        Args:
            file_path: Path to the file to stream
            encoding: Character encoding (auto-detected if None)

        Returns:
            A ContentStreamer instance for the file

        Raises:
            ValueError: If encoding cannot be detected or file is invalid

        """
        # Import here to avoid circular import
        from kp_ssf_tools.core.services.file_processing.streaming import (
            FileContentStreamer,
        )

        # Validate file exists
        if not self.file_validator.validate_file_exists(file_path):
            msg = f"File does not exist: {file_path}"
            raise ValueError(msg)

        # Auto-detect encoding if not provided
        if encoding is None:
            encoding = self.encoding_detector.detect_encoding(file_path)
            if encoding is None:
                msg = f"Could not detect encoding for file: {file_path}"
                raise ValueError(msg)

        return FileContentStreamer(file_path, encoding)

    def create_binary_streamer(
        self,
        file_path: Path,
        chunk_size: int = 4096,
    ) -> BinaryStreamerProtocol:
        """
        Create a binary streamer for efficient binary file processing.

        Args:
            file_path: Path to the file to stream
            chunk_size: Default chunk size for binary operations (default: 4KiB)

        Returns:
            A BinaryStreamerProtocol instance for the file

        Raises:
            ValueError: If file is invalid or inaccessible

        """
        # Import here to avoid circular import
        from kp_ssf_tools.core.services.file_processing.binary_streaming import (
            BinaryContentStreamer,
        )

        # Validate file exists
        if not self.file_validator.validate_file_exists(file_path):
            msg = f"File does not exist: {file_path}"
            raise ValueError(msg)

        return BinaryContentStreamer(file_path, chunk_size)
