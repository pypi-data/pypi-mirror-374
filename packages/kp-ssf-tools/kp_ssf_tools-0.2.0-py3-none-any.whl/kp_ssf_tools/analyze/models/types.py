"""Types for entropy analysis models."""

from __future__ import annotations

from enum import StrEnum


class FileType(StrEnum):
    """File types for entropy analysis using Pygments lexer names where applicable."""

    # Programming languages (using Pygments lexer names)
    C = "C"
    CPP = "C++"
    CSHARP = "C#"
    DART = "Dart"
    GO = "Go"
    JAVA = "Java"
    JAVASCRIPT = "JavaScript"
    KOTLIN = "Kotlin"
    MATLAB = "MATLAB"
    PERL = "Perl"
    PHP = "PHP"
    PYTHON = "Python"
    R = "R"
    RUBY = "Ruby"
    RUST = "Rust"
    SCALA = "Scala"
    SQL = "SQL"
    SWIFT = "Swift"
    TYPESCRIPT = "TypeScript"
    VISUAL_BASIC = "Visual Basic"

    # Special content types
    DOCUMENTATION = "documentation"  # Plain text files, documentation
    BASE64_ENCODED = "base64_encoded"  # Custom
    ENCRYPTED = "encrypted"  # Custom
    HEX_ENCODED = "hex_encoded"  # Custom

    # Binary executables
    LINUX_ELF = "linux_elf"  # Custom
    MACOS_MACHO = "macos_macho"  # Custom
    WINDOWS_PE = "windows_pe"  # Custom

    # Fallback
    UNKNOWN = "unknown"

    @classmethod
    def from_pygments_lexer(cls, lexer_name: str) -> FileType:
        """
        Map Pygments lexer names to FileType enums.

        Handles multiple lexer names for the same language (e.g., "Python" vs "Python 3").

        Args:
            lexer_name: Name from Pygments lexer.name

        Returns:
            Corresponding FileType enum, defaults to UNKNOWN for unrecognized lexers

        """
        # Direct matches (most common case)
        for file_type in cls:
            if file_type.value == lexer_name:
                return file_type

        # Handle aliases and special cases
        lexer_aliases = {
            "Python 3": cls.PYTHON,
            "JavaScript+Lasso": cls.JAVASCRIPT,
            "VB.net": cls.VISUAL_BASIC,
            "Markdown": cls.DOCUMENTATION,
            "reStructuredText": cls.DOCUMENTATION,
            "Text only": cls.DOCUMENTATION,
        }

        return lexer_aliases.get(lexer_name, cls.UNKNOWN)


class EntropyLevel(StrEnum):
    """Entropy classification levels (thresholds are file-type adaptive)."""

    CRITICAL = "critical"  # Significantly above expected for file type
    HIGH = "high"  # Above normal range for file type
    MEDIUM_HIGH = "medium_high"  # Slightly elevated for file type
    MEDIUM = "medium"  # Normal range for file type
    LOW = "low"  # Below normal range for file type
    VERY_LOW = "very_low"  # Significantly below expected for file type

    @property
    def order(self) -> int:
        """
        Get the order of the entropy level.

        Higher levels have a higher order (e.g., CRITICAL > HIGH)
        """
        levels = list(type(self))
        return len(levels) - levels.index(self) - 1


class CryptoStructureType(StrEnum):
    """Types of cryptographic structures and credential patterns."""

    # Cryptographic structures
    AES_SBOX = "aes_sbox"
    DES_SBOX = "des_sbox"
    ROUND_CONSTANTS = "round_constants"
    GALOIS_FIELD = "galois_field"
    BASE64_DATA = "base64_data"
    HEX_ENCODED = "hex_encoded"
    PEM_STRUCTURE = "pem_structure"
    CRYPTO_FUNCTION = "crypto_function"
    HARDCODED_KEY = "hardcoded_key"

    # Credential patterns (PCI SSF 2.3.b requirement)
    COMMON_USERNAME = "common_username"
    COMMON_PASSWORD = "common_password"  # noqa: S105
    DEFAULT_CREDENTIAL = "default_credential"
    API_KEY_PATTERN = "api_key_pattern"
    DATABASE_CONNECTION = "database_connection"
    CREDENTIAL_PATTERN = "credential_pattern"


class ComplianceStatus(StrEnum):
    """PCI SSF compliance status levels."""

    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    REQUIRES_REVIEW = "requires_review"
    INSUFFICIENT_DATA = "insufficient_data"


class CredentialRiskLevel(StrEnum):
    """Risk levels for detected credentials."""

    CRITICAL = "critical"  # Confirmed high-value credentials
    HIGH = "high"  # Likely credentials with high impact
    MEDIUM = "medium"  # Potential credentials requiring review
    LOW = "low"  # Suspicious patterns, low confidence
    INFO = "info"  # Informational findings
