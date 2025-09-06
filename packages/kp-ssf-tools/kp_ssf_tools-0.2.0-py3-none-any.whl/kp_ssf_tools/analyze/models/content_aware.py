"""Content-Aware Thresholds module."""

from __future__ import annotations

from typing import cast

from kp_ssf_tools.analyze.models.types import FileType
from kp_ssf_tools.models.base import SSFToolsBaseModel


class ContentAwareThresholds(SSFToolsBaseModel):
    """File type-specific entropy thresholds loaded from configuration."""

    file_type: FileType
    expected_entropy: tuple[float, float]  # (mean, std_dev) for normal content
    very_low_threshold: float  # Below this = VERY_LOW
    low_threshold: float  # Below this = LOW
    medium_threshold: float  # Normal range center
    medium_high_threshold: float  # Above this = MEDIUM_HIGH
    high_threshold: float  # Above this = HIGH

    @classmethod
    def get_default_values(cls) -> dict[FileType, dict[str, object]]:
        """
        Default threshold values for configuration file generation.

        These values are derived from extensive academic research documented
        in docs/file-entropy-research.md, including:
        - Lyda & Hamrock (2007) IEEE foundational paper
        - Davies et al. (2022) NapierOne dataset (500,000+ files)
        - Practical Security Analytics (500,000 PE file analysis)
        - Multiple peer-reviewed studies with statistical validation

        Returns a dict suitable for YAML configuration file generation.
        """
        return {
            # Top 20 Programming Languages (2025 Rankings)
            FileType.PYTHON: {
                "expected_entropy": [
                    5.5,
                    0.8,
                ],  # Mean=5.5, StdDev=0.8
                "very_low_threshold": 4.0,  # Highly repetitive code
                "low_threshold": 5.0,  # Simple scripts, lots of comments
                "medium_threshold": 6.0,  # Typical Python code
                "medium_high_threshold": 6.8,  # Complex logic, minified
                "high_threshold": 7.2,  # Obfuscated/packed code | > Likely suspicious
            },
            FileType.JAVASCRIPT: {
                "expected_entropy": [
                    5.4,
                    0.8,
                ],  # Mean=5.4, StdDev=0.8
                "very_low_threshold": 4.0,  # Simple scripts
                "low_threshold": 4.9,  # Basic JS with comments
                "medium_threshold": 5.9,  # Typical JavaScript
                "medium_high_threshold": 6.8,  # Minified/complex
                "high_threshold": 7.2,  # Obfuscated code | > Likely suspicious
            },
            FileType.JAVA: {
                "expected_entropy": [
                    5.6,
                    0.7,
                ],  # Mean=5.6, StdDev=0.7
                "very_low_threshold": 4.0,  # Verbose Java patterns
                "low_threshold": 5.0,  # Simple classes
                "medium_threshold": 6.0,  # Typical Java code
                "medium_high_threshold": 6.8,  # Complex enterprise code
                "high_threshold": 7.2,  # Bytecode/obfuscated | > Likely suspicious
            },
            FileType.CPP: {
                "expected_entropy": [
                    5.8,
                    0.9,
                ],  # Mean=5.8, StdDev=0.9
                "very_low_threshold": 4.0,  # Header files
                "low_threshold": 5.0,  # Simple implementations
                "medium_threshold": 6.2,  # Typical C++ code
                "medium_high_threshold": 7.0,  # Template-heavy code
                "high_threshold": 7.3,  # Compiled/obfuscated | > Likely suspicious
            },
            FileType.C: {
                "expected_entropy": [
                    5.7,
                    0.9,
                ],  # Mean=5.7, StdDev=0.9
                "very_low_threshold": 4.0,  # Header files
                "low_threshold": 5.0,  # Simple C code
                "medium_threshold": 6.1,  # Typical C programs
                "medium_high_threshold": 6.9,  # Complex system code
                "high_threshold": 7.3,  # Compiled/obfuscated | > Likely suspicious
            },
            FileType.CSHARP: {
                "expected_entropy": [
                    5.6,
                    0.8,
                ],  # Mean=5.6, StdDev=0.8
                "very_low_threshold": 4.0,  # Simple classes
                "low_threshold": 5.0,  # Basic C# code
                "medium_threshold": 6.0,  # Typical C# applications
                "medium_high_threshold": 6.8,  # Complex .NET code
                "high_threshold": 7.2,  # IL bytecode/obfuscated | > Likely suspicious
            },
            FileType.TYPESCRIPT: {
                "expected_entropy": [
                    5.4,
                    0.8,
                ],  # Mean=5.4, StdDev=0.8
                "very_low_threshold": 4.0,  # Type definitions
                "low_threshold": 4.9,  # Simple TypeScript
                "medium_threshold": 5.9,  # Typical TS code
                "medium_high_threshold": 6.8,  # Complex/transpiled
                "high_threshold": 7.2,  # Obfuscated output | > Likely suspicious
            },
            FileType.PHP: {
                "expected_entropy": [
                    5.3,
                    0.8,
                ],  # Mean=5.3, StdDev=0.8
                "very_low_threshold": 4.0,  # HTML mixed PHP
                "low_threshold": 4.8,  # Simple PHP scripts
                "medium_threshold": 5.8,  # Typical PHP code
                "medium_high_threshold": 6.7,  # Complex frameworks
                "high_threshold": 7.1,  # Obfuscated PHP | > Likely suspicious
            },
            FileType.GO: {
                "expected_entropy": [
                    5.5,
                    0.7,
                ],  # Mean=5.5, StdDev=0.7
                "very_low_threshold": 4.0,  # Simple Go code
                "low_threshold": 5.0,  # Basic programs
                "medium_threshold": 6.0,  # Typical Go code
                "medium_high_threshold": 6.8,  # Complex concurrent code
                "high_threshold": 7.2,  # Compiled binary data | > Likely suspicious
            },
            FileType.SQL: {
                "expected_entropy": [
                    5.2,
                    0.9,
                ],  # Mean=5.2, StdDev=0.9
                "very_low_threshold": 3.8,  # Simple queries
                "low_threshold": 4.7,  # Basic SQL statements
                "medium_threshold": 5.7,  # Complex queries
                "medium_high_threshold": 6.6,  # Stored procedures
                "high_threshold": 7.0,  # Obfuscated SQL | > Likely suspicious
            },
            FileType.RUST: {
                "expected_entropy": [
                    5.7,
                    0.8,
                ],  # Mean=5.7, StdDev=0.8
                "very_low_threshold": 4.0,  # Simple Rust code
                "low_threshold": 5.0,  # Basic implementations
                "medium_threshold": 6.1,  # Typical Rust code
                "medium_high_threshold": 6.9,  # Complex unsafe code
                "high_threshold": 7.3,  # Compiled/obfuscated | > Likely suspicious
            },
            FileType.SWIFT: {
                "expected_entropy": [
                    5.5,
                    0.8,
                ],  # Mean=5.5, StdDev=0.8
                "very_low_threshold": 4.0,  # Simple Swift code
                "low_threshold": 5.0,  # Basic iOS code
                "medium_threshold": 6.0,  # Typical Swift apps
                "medium_high_threshold": 6.8,  # Complex frameworks
                "high_threshold": 7.2,  # Compiled/obfuscated | > Likely suspicious
            },
            FileType.KOTLIN: {
                "expected_entropy": [
                    5.5,
                    0.8,
                ],  # Mean=5.5, StdDev=0.8
                "very_low_threshold": 4.0,  # Simple Kotlin code
                "low_threshold": 5.0,  # Basic Android code
                "medium_threshold": 6.0,  # Typical Kotlin apps
                "medium_high_threshold": 6.8,  # Complex coroutines
                "high_threshold": 7.2,  # Bytecode/obfuscated | > Likely suspicious
            },
            FileType.RUBY: {
                "expected_entropy": [
                    5.3,
                    0.8,
                ],  # Mean=5.3, StdDev=0.8
                "very_low_threshold": 4.0,  # Simple Ruby scripts
                "low_threshold": 4.8,  # Basic Rails code
                "medium_threshold": 5.8,  # Typical Ruby code
                "medium_high_threshold": 6.7,  # Complex metaprogramming
                "high_threshold": 7.1,  # Obfuscated Ruby | > Likely suspicious
            },
            FileType.R: {
                "expected_entropy": [
                    5.4,
                    0.9,
                ],  # Mean=5.4, StdDev=0.9
                "very_low_threshold": 3.9,  # Simple R scripts
                "low_threshold": 4.8,  # Basic statistics
                "medium_threshold": 5.9,  # Typical R analysis
                "medium_high_threshold": 6.8,  # Complex models
                "high_threshold": 7.1,  # Compiled R code | > Likely suspicious
            },
            FileType.VISUAL_BASIC: {
                "expected_entropy": [
                    5.2,
                    0.8,
                ],  # Mean=5.2, StdDev=0.8
                "very_low_threshold": 3.9,  # Simple VB code
                "low_threshold": 4.7,  # Basic VB.NET
                "medium_threshold": 5.7,  # Typical VB apps
                "medium_high_threshold": 6.6,  # Complex forms
                "high_threshold": 7.0,  # Obfuscated VB | > Likely suspicious
            },
            FileType.SCALA: {
                "expected_entropy": [
                    5.6,
                    0.8,
                ],  # Mean=5.6, StdDev=0.8
                "very_low_threshold": 4.0,  # Simple Scala code
                "low_threshold": 5.0,  # Basic functional code
                "medium_threshold": 6.0,  # Typical Scala apps
                "medium_high_threshold": 6.8,  # Complex Spark code
                "high_threshold": 7.2,  # Bytecode/obfuscated | > Likely suspicious
            },
            FileType.MATLAB: {
                "expected_entropy": [
                    5.4,
                    0.9,
                ],  # Mean=5.4, StdDev=0.9
                "very_low_threshold": 3.9,  # Simple scripts
                "low_threshold": 4.8,  # Basic computations
                "medium_threshold": 5.9,  # Typical MATLAB code
                "medium_high_threshold": 6.8,  # Complex algorithms
                "high_threshold": 7.1,  # Compiled MEX files | > Likely suspicious
            },
            FileType.PERL: {
                "expected_entropy": [
                    5.4,
                    0.9,
                ],  # Mean=5.4, StdDev=0.9
                "very_low_threshold": 3.9,  # Simple Perl scripts
                "low_threshold": 4.8,  # Basic regex code
                "medium_threshold": 5.9,  # Typical Perl code
                "medium_high_threshold": 6.8,  # Complex one-liners
                "high_threshold": 7.1,  # Obfuscated Perl | > Likely suspicious
            },
            FileType.DART: {
                "expected_entropy": [
                    5.5,
                    0.8,
                ],  # Mean=5.5, StdDev=0.8
                "very_low_threshold": 4.0,  # Simple Dart code
                "low_threshold": 5.0,  # Basic Flutter widgets
                "medium_threshold": 6.0,  # Typical Dart apps
                "medium_high_threshold": 6.8,  # Complex async code
                "high_threshold": 7.2,  # Compiled/obfuscated | > Likely suspicious
            },
            # Documentation Files
            FileType.DOCUMENTATION: {
                "expected_entropy": [
                    4.8,
                    0.65,
                ],  # Mean=4.8, StdDev=0.65 (combined plain/markdown)
                "very_low_threshold": 3.55,  # Highly repetitive text
                "low_threshold": 4.25,  # Simple documentation
                "medium_threshold": 5.1,  # Typical documentation
                "medium_high_threshold": 5.65,  # Technical docs with code
                "high_threshold": 6.15,  # Mixed content | Anomalous for docs
            },
            # Binary Executables
            FileType.WINDOWS_PE: {
                "expected_entropy": [
                    6.0,
                    1.2,
                ],  # Mean=6.0, StdDev=1.2
                "very_low_threshold": 4.5,  # Text sections
                "low_threshold": 5.2,  # Code sections
                "medium_threshold": 6.5,  # Typical PE files
                "medium_high_threshold": 7.0,  # Complex binaries
                "high_threshold": 7.2,  # Packed/compressed | > Likely suspicious
            },
            FileType.MACOS_MACHO: {
                "expected_entropy": [
                    5.9,
                    1.2,
                ],  # Mean=5.9, StdDev=1.2
                "very_low_threshold": 4.5,  # Text sections
                "low_threshold": 5.2,  # Code sections
                "medium_threshold": 6.4,  # Typical MachO files
                "medium_high_threshold": 6.9,  # Universal binaries
                "high_threshold": 7.2,  # Packed/compressed | > Likely suspicious
            },
            FileType.LINUX_ELF: {
                "expected_entropy": [
                    5.8,
                    1.1,
                ],  # Mean=5.8, StdDev=1.1
                "very_low_threshold": 4.5,  # Text sections
                "low_threshold": 5.1,  # Code sections
                "medium_threshold": 6.3,  # Typical ELF files
                "medium_high_threshold": 6.8,  # Complex binaries
                "high_threshold": 7.2,  # Packed/compressed | > Likely suspicious
            },
            # Encrypted/Suspicious Content
            FileType.ENCRYPTED: {
                "expected_entropy": [
                    7.99,
                    0.01,
                ],  # Mean=7.99, StdDev=0.01 (AES validated)
                "very_low_threshold": 7.8,  # Weak/broken encryption
                "low_threshold": 7.85,  # Poor encryption
                "medium_threshold": 7.9,  # Possible encryption
                "medium_high_threshold": 7.95,  # Likely encrypted
                "high_threshold": 7.98,  # Strong encryption | > Max entropy
            },
            FileType.BASE64_ENCODED: {
                "expected_entropy": [
                    6.0,
                    0.3,
                ],  # Mean=6.0, StdDev=0.3
                "very_low_threshold": 5.2,  # Partial encoding
                "low_threshold": 5.5,  # Simple base64
                "medium_threshold": 6.0,  # Typical base64
                "medium_high_threshold": 6.3,  # Complex encoded data
                "high_threshold": 6.5,  # Encrypted then encoded | > Suspicious encoding
            },
            FileType.HEX_ENCODED: {
                "expected_entropy": [
                    4.0,
                    0.2,
                ],  # Mean=4.0, StdDev=0.2
                "very_low_threshold": 3.5,  # Partial hex
                "low_threshold": 3.7,  # Simple hex strings
                "medium_threshold": 4.0,  # Typical hex encoding
                "medium_high_threshold": 4.2,  # Complex hex data
                "high_threshold": 4.4,  # Anomalous hex | > Suspicious pattern
            },
            # Unknown file types - Conservative thresholds
            FileType.UNKNOWN: {
                "expected_entropy": [
                    5.5,
                    1.5,
                ],  # Mean=5.5, StdDev=1.5 (conservative mixed content)
                "very_low_threshold": 3.0,  # Likely text/structured
                "low_threshold": 4.5,  # Probable code/data
                "medium_threshold": 6.0,  # Typical binary content
                "medium_high_threshold": 7.0,  # Complex binary/media
                "high_threshold": 7.2,  # Boundary suspicious | > Conservative threshold
            },
        }

    @classmethod
    def get_default_models(cls) -> dict[FileType, ContentAwareThresholds]:
        """
        Get pre-built Pydantic model instances for all file types.

        Returns validated ContentAwareThresholds models instead of raw dicts.
        Use this method for runtime threshold management to avoid dict-to-model conversion.

        """
        models = {}
        for file_type, data in cls.get_default_values().items():
            # Cast values from object to proper types
            expected_entropy = data["expected_entropy"]
            if isinstance(expected_entropy, list | tuple):
                float_values = [float(x) for x in expected_entropy]
                # Ensure we have exactly 2 values for tuple[float, float]
                expected_tuple_length = 2
                if len(float_values) >= expected_tuple_length:
                    entropy_tuple = (float_values[0], float_values[1])
                else:
                    entropy_tuple = (0.0, 8.0)  # fallback
            else:
                entropy_tuple = (0.0, 8.0)  # fallback

            models[file_type] = cls(
                file_type=file_type,
                expected_entropy=entropy_tuple,
                very_low_threshold=cast("float", data["very_low_threshold"]),
                low_threshold=cast("float", data["low_threshold"]),
                medium_threshold=cast("float", data["medium_threshold"]),
                medium_high_threshold=cast("float", data["medium_high_threshold"]),
                high_threshold=cast("float", data["high_threshold"]),
            )
        return models

    @classmethod
    def for_file_type(cls, file_type: FileType) -> ContentAwareThresholds:
        """
        Factory method to create a threshold model for a specific file type.

        Args:
            file_type: The file type to get thresholds for

        Returns:
            ContentAwareThresholds model instance with validated data

        Raises:
            KeyError: If file_type is not supported

        """
        defaults = cls.get_default_values()
        if file_type not in defaults:
            # Return sensible defaults for unknown file types
            return cls(
                file_type=file_type,
                expected_entropy=(5.5, 1.0),
                very_low_threshold=4.0,
                low_threshold=5.0,
                medium_threshold=6.0,
                medium_high_threshold=6.8,
                high_threshold=7.2,
            )

        data = defaults[file_type]
        # Cast values from object to proper types
        expected_entropy = data["expected_entropy"]
        if isinstance(expected_entropy, list | tuple):
            float_values = [float(x) for x in expected_entropy]
            # Ensure we have exactly 2 values for tuple[float, float]
            expected_tuple_length = 2
            if len(float_values) >= expected_tuple_length:
                entropy_tuple = (float_values[0], float_values[1])
            else:
                entropy_tuple = (0.0, 8.0)  # fallback
        else:
            entropy_tuple = (0.0, 8.0)  # fallback

        return cls(
            file_type=file_type,
            expected_entropy=entropy_tuple,
            very_low_threshold=cast("float", data["very_low_threshold"]),
            low_threshold=cast("float", data["low_threshold"]),
            medium_threshold=cast("float", data["medium_threshold"]),
            medium_high_threshold=cast("float", data["medium_high_threshold"]),
            high_threshold=cast("float", data["high_threshold"]),
        )
