"""Detect-secrets backend implementation for credential detection."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from kp_ssf_tools.analyze.models import CredentialAnalysisResult, CredentialPattern
    from kp_ssf_tools.analyze.services.interfaces import CredentialScanOptions
    from kp_ssf_tools.core.services.file_processing import (
        FileDiscoveryService,
        FileProcessingService,
    )
    from kp_ssf_tools.core.services.rich_output import RichOutputService
    from kp_ssf_tools.core.services.timestamp import TimestampProtocol

from kp_ssf_tools.analyze.models import (
    CredentialAnalysisResult,
    CredentialPattern,
)
from kp_ssf_tools.analyze.models.types import (
    CredentialRiskLevel,
)


class DetectSecretsCredentialService:
    """Credential detection service using detect-secrets as backend."""

    def __init__(
        self,
        rich_output: RichOutputService,
        timestamp_service: TimestampProtocol,
        file_discovery: FileDiscoveryService,
        file_processing: FileProcessingService,
    ) -> None:
        """
        Initialize the detect-secrets credential detection service.

        Args:
            rich_output: Service for displaying progress and results
            timestamp_service: Service for timestamp operations
            file_discovery: Service for discovering files to analyze
            file_processing: Service for file type detection and processing

        """
        self.rich_output: RichOutputService = rich_output
        self.timestamp: TimestampProtocol = timestamp_service
        self.file_discovery: FileDiscoveryService = file_discovery
        self.file_processing: FileProcessingService = file_processing

    def analyze_files(
        self,
        target_paths: list[Path],
        config: dict[str, Any],
        options: CredentialScanOptions,
    ) -> CredentialAnalysisResult:
        """
        Analyze files using detect-secrets and return results in existing format.

        Args:
            target_paths: List of file or directory paths to analyze
            config: Analysis configuration
            options: Scanning options and parameters

        Returns:
            Analysis result containing detected patterns

        """
        self.rich_output.info("Starting detect-secrets credential analysis...")

        # Run detect-secrets scan and get JSON output directly
        secrets_data = self._run_scan(target_paths, config, options)

        # Convert detect-secrets results to our format
        patterns = self._convert_to_patterns(secrets_data, options.context_lines)

        # Extract all processed files from detect-secrets results
        processed_files = [
            Path(file_path) for file_path in secrets_data.get("results", {})
        ]

        # Return single file result or first target if multiple
        primary_target = target_paths[0] if target_paths else Path()

        return CredentialAnalysisResult(
            file_path=primary_target,
            patterns=patterns,
            total_patterns=len(patterns),
            processed_files=processed_files,
        )

    def _run_scan(
        self,
        target_paths: list[Path],
        config: dict[str, Any],
        options: CredentialScanOptions,
    ) -> dict[str, Any]:
        """Run detect-secrets scan and return JSON results."""
        # Build base command for direct JSON output
        cmd = ["detect-secrets", "scan"]

        # Add configuration-based options
        cmd.extend(self._build_config_options(config))

        # Add target paths
        cmd.extend(self._build_target_options(target_paths, options))

        # Execute detect-secrets scan and capture JSON output
        return self._execute_scan_command(cmd)

    def _build_config_options(self, config: dict[str, Any]) -> list[str]:
        """Build configuration options for detect-secrets command."""
        options = []
        credential_config = config.get("credentials", {})

        # Configure entropy limits if specified
        if "entropy_limits" in credential_config:
            limits = credential_config["entropy_limits"]
            if "base64" in limits:
                options.extend(["--base64-limit", str(limits["base64"])])
            if "hex" in limits:
                options.extend(["--hex-limit", str(limits["hex"])])

        # Add exclude patterns if configured
        if "exclude_patterns" in credential_config:
            patterns = credential_config["exclude_patterns"]
            if "files" in patterns:
                options.extend(["--exclude-files", patterns["files"]])
            if "lines" in patterns:
                options.extend(["--exclude-lines", patterns["lines"]])
            if "secrets" in patterns:
                options.extend(["--exclude-secrets", patterns["secrets"]])

        # Add word list if configured
        if "word_list_path" in credential_config:
            word_list_path = Path(credential_config["word_list_path"])
            if word_list_path.exists():
                options.extend(["--word-list", str(word_list_path)])

        return options

    def _build_target_options(
        self,
        target_paths: list[Path],
        options: CredentialScanOptions,
    ) -> list[str]:
        """Build target path options for detect-secrets command."""
        cmd_options = []

        for target_path in target_paths:
            if target_path.is_dir() and not options.recursive:
                # For non-recursive directory scanning
                cmd_options.append("--all-files")
            cmd_options.append(str(target_path))

        return cmd_options

    def _execute_scan_command(self, cmd: list[str]) -> dict[str, Any]:
        """Execute the detect-secrets scan command safely and return JSON results."""
        # Validate command for security - ensure it starts with detect-secrets
        if not cmd or cmd[0] != "detect-secrets":
            error_msg = "Invalid command: must start with 'detect-secrets'"
            self.rich_output.error(error_msg)
            raise ValueError(error_msg)

        try:
            self.rich_output.debug(f"Running: {' '.join(cmd)}")
            # Security: Command is constructed internally with validated components
            result = subprocess.run(  # noqa: S603
                cmd,
                capture_output=True,
                text=True,
                check=False,  # Don't raise on non-zero exit (normal for secrets found)
                cwd=Path.cwd(),
                timeout=300,  # 5 minute timeout for safety
            )

            if result.returncode not in (0, 1):  # 0=no secrets, 1=secrets found
                error_msg = f"detect-secrets failed: {result.stderr}"
                self.rich_output.error(error_msg)
                raise RuntimeError(error_msg)

            self.rich_output.debug(
                f"detect-secrets scan completed with exit code {result.returncode}",
            )

            # Parse JSON output from stdout
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError as e:
                self.rich_output.error(
                    f"Failed to parse detect-secrets JSON output: {e}",
                )
                return {"results": {}}

        except FileNotFoundError as e:
            error_msg = (
                "detect-secrets not found. Please install: pip install detect-secrets"
            )
            self.rich_output.error(error_msg)
            raise RuntimeError(error_msg) from e
        except subprocess.TimeoutExpired as e:
            error_msg = "detect-secrets scan timed out after 5 minutes"
            self.rich_output.error(error_msg)
            raise RuntimeError(error_msg) from e

    def _parse_baseline(self, baseline_file: Path) -> dict[str, Any]:
        """Parse the detect-secrets baseline JSON file."""
        try:
            with baseline_file.open(encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            self.rich_output.error(f"Failed to parse baseline file: {e}")
            return {"results": {}}

    def _convert_to_patterns(
        self,
        secrets_data: dict[str, Any],
        context_lines: int,
    ) -> list[CredentialPattern]:
        """Convert detect-secrets results to CredentialPattern objects."""
        patterns: list[CredentialPattern] = []

        results = secrets_data.get("results", {})

        for file_path_str, file_secrets in results.items():
            file_path = Path(file_path_str)

            for secret in file_secrets:
                detector_type = secret.get("type", "unknown")
                risk_level = self._determine_risk_level_from_detector(
                    detector_type,
                    secret,
                )

                # Extract context lines around the secret
                context_lines_data = self._extract_context(
                    file_path,
                    secret,
                    context_lines,
                )
                context_before = (
                    "\n".join(context_lines_data[:context_lines])
                    if context_lines_data
                    else ""
                )
                context_after = (
                    "\n".join(context_lines_data[context_lines + 1 :])
                    if context_lines_data
                    else ""
                )

                pattern = CredentialPattern(
                    # BinaryLocationMixin fields
                    offset=0,  # detect-secrets doesn't provide byte offset
                    size=len(
                        secret.get("hashed_secret", ""),
                    ),  # Use hash length as approximation
                    confidence=1.0,  # detect-secrets results are high confidence
                    # TextLocationMixin fields
                    line_start=secret.get("line_number", 0),
                    line_end=secret.get("line_number", 0),
                    column_start=None,  # detect-secrets doesn't provide column info
                    column_end=None,
                    # CredentialLocationMixin fields
                    context_before=context_before,
                    context_after=context_after,
                    # DetectedCredential fields
                    pattern_type=detector_type,  # Use detector type directly as pattern type
                    risk_level=risk_level,
                    value=f"[DETECTED:{secret.get('type', 'SECRET')}]",  # detect-secrets only provides hashed values
                    detection_method="detect-secrets",
                    # CredentialPattern specific fields
                    file_path=file_path,  # Include file path in each pattern
                    regex_pattern=None,
                    wordlist_source=None,
                )
                patterns.append(pattern)

        return patterns

    def _determine_risk_level_from_detector(
        self,
        detector_type: str,
        secret: dict[str, Any],
    ) -> CredentialRiskLevel:
        """Determine risk level based on detect-secrets detector type and secret properties."""
        # Check if secret is verified (if available)
        is_verified = secret.get("is_verified", False)

        if is_verified:
            return CredentialRiskLevel.CRITICAL

        # High risk for API keys and private keys
        high_risk_detectors = {
            "AWS Access Key",
            "Azure Storage Account access key",
            "GitHub Token",
            "GitLab Token",
            "OpenAI API Key",
            "Stripe Access Key",
            "Private Key",
            "Discord Bot Token",
            "Mailchimp Access Key",
            "NPM tokens",
            "PyPI upload token",
            "SendGrid API Key",
            "Slack Token",
            "JWT Token",
            "IBM Cloud IAM Key",
            "Telegram Bot Token",
            "Twilio API Key",
        }

        if detector_type in high_risk_detectors:
            return CredentialRiskLevel.HIGH

        # Medium risk for authentication patterns and high entropy strings
        medium_risk_detectors = {
            "Basic Auth Credentials",
            "Keyword",  # Keywords often indicate passwords
        }

        if detector_type in medium_risk_detectors:
            return CredentialRiskLevel.MEDIUM

        # Low risk for entropy-based detectors (less specific)
        low_risk_detectors = {
            "Base64 High Entropy String",
            "Hex High Entropy String",
        }

        if detector_type in low_risk_detectors:
            return CredentialRiskLevel.LOW

        # Default to LOW for unknown detectors
        return CredentialRiskLevel.LOW

    def _extract_context(
        self,
        file_path: Path,
        secret: dict[str, Any],
        context_lines: int,
    ) -> list[str]:
        """Extract context lines around the detected secret."""
        try:
            line_number = secret.get("line_number", 1)
            with file_path.open(encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            start_line = max(0, line_number - context_lines - 1)
            end_line = min(len(lines), line_number + context_lines)

            return [line.rstrip() for line in lines[start_line:end_line]]

        except (OSError, UnicodeDecodeError):
            # If we can't read the file, return empty context
            return []
