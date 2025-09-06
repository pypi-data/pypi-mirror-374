"""Language detection service using Pygments."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from kp_ssf_tools.analyze.models.types import FileType

if TYPE_CHECKING:
    from pathlib import Path


class PygmentsLanguageDetector:
    """
    Language detection using Pygments lexer analysis.

    Provides accurate language detection for source code files
    based on file extensions, content analysis, and syntax patterns.
    Uses FileType.from_pygments_lexer() for clean mapping.
    """

    def __init__(self) -> None:
        """Initialize the language detector."""
        # Lazy import to avoid dependency issues
        self._pygments: Any = None

    def detect_language(
        self,
        file_path: Path,
        content: bytes | None = None,
    ) -> FileType:
        """
        Detect programming language using Pygments lexer analysis.

        Args:
            file_path: Path to analyze
            content: Optional file content

        Returns:
            Detected FileType using Pygments lexer names

        """
        try:
            # Lazy import Pygments
            if self._pygments is None:
                import pygments.lexers
                import pygments.util

                self._pygments = pygments

            # Read content if not provided
            if content is None:
                try:
                    content = file_path.read_bytes()
                except (OSError, PermissionError):
                    return FileType.UNKNOWN

            # Try to guess lexer from filename and content
            try:
                if self._pygments and hasattr(self._pygments, "lexers"):
                    lexer = self._pygments.lexers.guess_lexer_for_filename(
                        file_path.name,
                        content.decode("utf-8", errors="ignore"),
                        stripnl=False,
                    )
                    # Use the new clean mapping method
                    return FileType.from_pygments_lexer(lexer.name)

            except (AttributeError, ImportError, ValueError):
                # Pygments errors (ClassNotFound inherits from ValueError), fallback to extension detection
                return self._detect_by_extension(file_path)

        except ImportError:
            # Pygments not available, fallback to extension detection
            return self._detect_by_extension(file_path)

        # Fallback if all else fails
        return self._detect_by_extension(file_path)

    def _detect_by_extension(self, file_path: Path) -> FileType:
        """Fallback language detection using file extensions."""
        extension_mapping = {
            ".py": FileType.PYTHON,
            ".js": FileType.JAVASCRIPT,
            ".ts": FileType.TYPESCRIPT,
            ".java": FileType.JAVA,
            ".cpp": FileType.CPP,
            ".cxx": FileType.CPP,
            ".cc": FileType.CPP,
            ".c": FileType.C,
            ".cs": FileType.CSHARP,
            ".go": FileType.GO,
            ".rs": FileType.RUST,
            ".swift": FileType.SWIFT,
            ".kt": FileType.KOTLIN,
            ".scala": FileType.SCALA,
            ".rb": FileType.RUBY,
            ".php": FileType.PHP,
            ".pl": FileType.PERL,
            ".r": FileType.R,
            ".sql": FileType.SQL,
            ".m": FileType.MATLAB,
            ".dart": FileType.DART,
            ".vb": FileType.VISUAL_BASIC,
            # Only map known documentation file extensions
            ".md": FileType.DOCUMENTATION,
            ".txt": FileType.DOCUMENTATION,
            ".rst": FileType.DOCUMENTATION,
        }

        suffix = file_path.suffix.lower()
        return extension_mapping.get(suffix, FileType.UNKNOWN)
