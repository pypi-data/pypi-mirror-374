"""MIME type detection service using puremagic and python-magic libraries."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

import puremagic

from kp_ssf_tools.core.services.file_processing.interfaces import MimeTypeDetector

# Try to import python-magic with fallback handling
try:
    import magic

    PYTHON_MAGIC_AVAILABLE = True
except ImportError:
    PYTHON_MAGIC_AVAILABLE = False
    magic = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)


class PureMagicMimeDetector(MimeTypeDetector):
    """
    MIME type detector using the puremagic library.

    This service provides file type detection by examining file contents
    rather than relying on file extensions. It uses magic numbers and
    file signatures to accurately identify file types.
    """

    def __init__(self, *, use_magic_file: bool = True) -> None:
        """
        Initialize the MIME type detector.

        Args:
            use_magic_file: Whether to use the magic file database for detection
                          (default: True for better accuracy)

        """
        self.use_magic_file = use_magic_file

    def detect_mime_type(self, file_path: Path) -> str | None:
        """
        Detect the MIME type of a file using content analysis.

        Args:
            file_path: Path to the file to analyze

        Returns:
            The detected MIME type string, or None if detection fails

        Raises:
            FileNotFoundError: If the file does not exist
            PermissionError: If the file cannot be read

        """
        if not file_path.exists():
            msg = f"File not found: {file_path}"
            raise FileNotFoundError(msg)

        if not file_path.is_file():
            return None

        try:
            # Handle empty files gracefully
            if file_path.stat().st_size == 0:
                return "application/x-empty"

            # Use puremagic to detect the MIME type directly from file
            mime_type = puremagic.from_file(file_path, mime=True)
        except (OSError, PermissionError) as e:
            msg = f"Cannot read file {file_path}: {e}"
            raise PermissionError(msg) from e
        except (
            ImportError,
            AttributeError,
            TypeError,
            ValueError,
            puremagic.PureError,
            Exception,
        ):
            # If puremagic fails for any reason (including empty files), return None
            return None
        else:
            return mime_type if mime_type else None

    def is_text_file(self, file_path: Path) -> bool:
        """
        Check if a file is a text file based on its MIME type.

        Args:
            file_path: Path to the file to check

        Returns:
            True if the file is detected as a text file, False otherwise

        """
        try:
            mime_type = self.detect_mime_type(file_path)
            if not mime_type:
                return False

            # Common text MIME types
            text_mime_prefixes = [
                "text/",
                "application/json",
                "application/xml",
                "application/yaml",
                "application/toml",
                "application/javascript",
                "application/x-sh",
                "application/x-shellscript",
            ]

            # Additional specific text types
            text_mime_types = {
                "application/x-empty",  # Empty files
                "inode/x-empty",  # Empty files (alternative)
            }

            mime_lower = mime_type.lower()

            return (
                any(mime_lower.startswith(prefix) for prefix in text_mime_prefixes)
                or mime_lower in text_mime_types
            )

        except (FileNotFoundError, PermissionError):
            return False

    def is_binary_file(self, file_path: Path) -> bool:
        """
        Check if a file is a binary file based on its MIME type.

        Args:
            file_path: Path to the file to check

        Returns:
            True if the file is detected as a binary file, False otherwise

        """
        try:
            mime_type = self.detect_mime_type(file_path)
            if not mime_type:
                # If we can't detect the MIME type, assume it's binary for safety
                return True

            # If it's a text file, it's not binary
            return not self.is_text_file(file_path)

        except (FileNotFoundError, PermissionError):
            return False


class LibmagicMimeDetector(MimeTypeDetector):
    """
    MIME type detector using the python-magic library (libmagic).

    This service provides enhanced file type detection using libmagic,
    which is more accurate and comprehensive than puremagic. It falls
    back to PureMagicMimeDetector if python-magic is not available or
    fails to initialize.

    Note:
        On Windows, this requires the python-magic-bin package to provide
        the necessary libmagic.dll file.

    """

    def __init__(self, *, use_magic_file: bool = True) -> None:
        """
        Initialize the MIME type detector.

        Args:
            use_magic_file: Whether to use the magic file database for detection
                          (default: True for better accuracy)

        """
        self.use_magic_file = use_magic_file
        self._magic_mime: object | None = None
        self._fallback_detector = PureMagicMimeDetector(use_magic_file=use_magic_file)
        self._initialize_magic()

    def _initialize_magic(self) -> None:
        """Initialize the python-magic library if available."""
        if not PYTHON_MAGIC_AVAILABLE or magic is None:
            return

        try:
            # Initialize magic for MIME type detection
            self._magic_mime = magic.Magic(mime=True)
        except (OSError, AttributeError, ImportError, RuntimeError) as e:
            # If initialization fails, we'll use the fallback
            logger.debug("Failed to initialize python-magic: %s", e)
            self._magic_mime = None

    def detect_mime_type(self, file_path: Path) -> str | None:
        """
        Detect the MIME type of a file using python-magic with fallback.

        Args:
            file_path: Path to the file to analyze

        Returns:
            The detected MIME type string, or None if detection fails

        Raises:
            FileNotFoundError: If the file does not exist
            PermissionError: If the file cannot be read

        """
        if not file_path.exists():
            msg = f"File not found: {file_path}"
            raise FileNotFoundError(msg)

        if not file_path.is_file():
            return None

        # Handle empty files gracefully
        if file_path.stat().st_size == 0:
            return "application/x-empty"

        # Try python-magic first if available
        if self._magic_mime is not None:
            try:
                mime_type = self._magic_mime.from_file(str(file_path))  # type: ignore[attr-defined]
                if mime_type and mime_type != "application/octet-stream":
                    return str(mime_type)
            except (OSError, AttributeError, UnicodeDecodeError, RuntimeError) as e:
                # If python-magic fails, fall back to puremagic
                logger.debug("python-magic detection failed for %s: %s", file_path, e)

        # Fall back to puremagic
        return self._fallback_detector.detect_mime_type(file_path)

    def is_text_file(self, file_path: Path) -> bool:
        """
        Check if a file is a text file based on its MIME type.

        Args:
            file_path: Path to the file to check

        Returns:
            True if the file is detected as a text file, False otherwise

        """
        try:
            mime_type = self.detect_mime_type(file_path)
            if not mime_type:
                return False

            # Common text MIME types
            text_mime_prefixes = [
                "text/",
                "application/json",
                "application/xml",
                "application/yaml",
                "application/toml",
                "application/javascript",
                "application/x-sh",
                "application/x-shellscript",
            ]

            # Additional specific text types
            text_mime_types = {
                "application/x-empty",  # Empty files
                "inode/x-empty",  # Empty files (alternative)
            }

            mime_lower = mime_type.lower()

            return (
                any(mime_lower.startswith(prefix) for prefix in text_mime_prefixes)
                or mime_lower in text_mime_types
            )

        except (FileNotFoundError, PermissionError):
            return False

    def is_binary_file(self, file_path: Path) -> bool:
        """
        Check if a file is a binary file based on its MIME type.

        Args:
            file_path: Path to the file to check

        Returns:
            True if the file is detected as a binary file, False otherwise

        """
        try:
            mime_type = self.detect_mime_type(file_path)
            if not mime_type:
                # If we can't detect the MIME type, assume it's binary for safety
                return True

            # If it's a text file, it's not binary
            return not self.is_text_file(file_path)

        except (FileNotFoundError, PermissionError):
            return False


class AutoMimeDetector(MimeTypeDetector):
    """
    Automatic MIME type detector that chooses the best available implementation.

    This detector automatically selects the most capable MIME detection library
    available on the system. It prefers libmagic (python-magic) when available,
    falls back to puremagic, and provides extension-based fallback as a last resort.

    This is the recommended detector for most use cases as it provides the best
    balance of accuracy and reliability across different environments.

    Args:
        enable_extension_fallback: Whether to use file extension as fallback
        prefer_python_magic: Whether to prefer python-magic over puremagic

    """

    def __init__(
        self,
        *,
        enable_extension_fallback: bool = True,
        prefer_python_magic: bool = True,
    ) -> None:
        """
        Initialize the enhanced MIME type detector.

        Args:
            enable_extension_fallback: Whether to use file extension as fallback
            prefer_python_magic: Whether to prefer python-magic over puremagic

        """
        self.enable_extension_fallback = enable_extension_fallback
        self.prefer_python_magic = prefer_python_magic

        # Type annotation for the primary detector
        self._primary_detector: MimeTypeDetector

        # Extension mappings for fallback detection
        self._extension_mappings = {
            ".txt": "text/plain",
            ".md": "text/markdown",
            ".py": "text/x-python",
            ".js": "application/javascript",
            ".html": "text/html",
            ".css": "text/css",
            ".json": "application/json",
            ".xml": "application/xml",
            ".yaml": "application/yaml",
            ".yml": "application/yaml",
            ".toml": "application/toml",
            ".csv": "text/csv",
            ".log": "text/plain",
            ".conf": "text/plain",
            ".cfg": "text/plain",
            ".ini": "text/plain",
        }

        # Initialize primary detector based on availability and preference
        if prefer_python_magic and PYTHON_MAGIC_AVAILABLE:
            try:
                self._primary_detector = LibmagicMimeDetector()
                self._detector_type = "python-magic"
            except (OSError, AttributeError, ImportError, RuntimeError) as e:
                logger.debug("Failed to initialize LibmagicMimeDetector: %s", e)
                self._primary_detector = PureMagicMimeDetector()
                self._detector_type = "puremagic"
        else:
            self._primary_detector = PureMagicMimeDetector()
            self._detector_type = "puremagic"

    @property
    def detector_type(self) -> str:
        """Get the type of the primary detector being used."""
        return self._detector_type

    def detect_mime_type(self, file_path: Path) -> str | None:
        """
        Detect MIME type using the best available detector.

        Args:
            file_path: Path to the file to analyze

        Returns:
            The detected MIME type string, or None if detection fails

        """
        if not file_path.exists():
            msg = f"File not found: {file_path}"
            raise FileNotFoundError(msg)

        # Try primary detector first
        try:
            mime_type = self._primary_detector.detect_mime_type(file_path)
            if mime_type:
                return mime_type
        except (FileNotFoundError, PermissionError, OSError, RuntimeError) as e:
            logger.debug("Primary detector failed for %s: %s", file_path, e)

        # Fall back to extension-based detection if enabled
        if self.enable_extension_fallback:
            extension = file_path.suffix.lower()
            return self._extension_mappings.get(extension)

        return None

    def is_text_file(self, file_path: Path) -> bool:
        """
        Check if a file is a text file using the best available detector.

        Args:
            file_path: Path to the file to check

        Returns:
            True if the file is detected as a text file, False otherwise

        """
        try:
            return self._primary_detector.is_text_file(file_path)
        except (FileNotFoundError, PermissionError, OSError, RuntimeError):
            if self.enable_extension_fallback:
                # Simple text file detection based on extension
                extension = file_path.suffix.lower()
                text_extensions = {
                    ".txt",
                    ".md",
                    ".py",
                    ".js",
                    ".html",
                    ".css",
                    ".json",
                    ".xml",
                    ".yaml",
                    ".yml",
                    ".toml",
                    ".csv",
                    ".log",
                    ".conf",
                    ".cfg",
                    ".ini",
                }
                return extension in text_extensions
            return False

    def is_binary_file(self, file_path: Path) -> bool:
        """
        Check if a file is a binary file using the best available detector.

        Args:
            file_path: Path to the file to check

        Returns:
            True if the file is detected as a binary file, False otherwise

        """
        try:
            return self._primary_detector.is_binary_file(file_path)
        except (FileNotFoundError, PermissionError, OSError, RuntimeError):
            if self.enable_extension_fallback:
                # Simple binary file detection based on extension
                extension = file_path.suffix.lower()
                text_extensions = {
                    ".txt",
                    ".md",
                    ".py",
                    ".js",
                    ".html",
                    ".css",
                    ".json",
                    ".xml",
                    ".yaml",
                    ".yml",
                    ".toml",
                    ".csv",
                    ".log",
                    ".conf",
                    ".cfg",
                    ".ini",
                }
                return extension not in text_extensions
            return True  # Default to binary for safety
