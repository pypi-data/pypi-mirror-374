"""Utility commands for diagnosing application behavior."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import rich_click as click
from dependency_injector.wiring import Provide, inject
from rich.table import Table

from kp_ssf_tools.containers.application import ApplicationContainer

if TYPE_CHECKING:
    from kp_ssf_tools.core.services.file_processing.discovery import (
        FileDiscoveryService,
    )
    from kp_ssf_tools.core.services.file_processing.service import (
        FileProcessingService,
    )
    from kp_ssf_tools.core.services.rich_output.service import RichOutputService


@click.group(name="utils")
def utils_group() -> None:
    """Utility commands for diagnosing application behavior."""


@utils_group.command("file-info")
@click.argument("target", type=str)
@click.option(
    "--no-recurse",
    is_flag=True,
    help="Disable recursive directory analysis (analyze current directory only)",
)
@inject
def file_info(
    target: str,
    *,
    no_recurse: bool,
    file_discovery: FileDiscoveryService = Provide[
        ApplicationContainer.core.file_discoverer
    ],
    file_processing: FileProcessingService = Provide[
        ApplicationContainer.core.file_processing
    ],
    rich_output: RichOutputService = Provide[ApplicationContainer.core.rich_output],
) -> None:
    """
    Display file analysis information including MIME type, encoding, and language detection.

    Shows diagnostic information about how the application analyzes files,
    including file discovery results and detection capabilities.

    **Arguments:**
    ```
    TARGET                  Path to file/directory or glob pattern to analyze
    ```

    **Examples:**
    ```
    # Analyze a single file
    ssf_tools utils file-info document.pdf

    # Analyze all Python files in current directory
    ssf_tools utils file-info "*.py"

    # Analyze all files recursively in a directory
    ssf_tools utils file-info /path/to/data

    # Analyze specific file types in a directory
    ssf_tools utils file-info "./logs/*.log"

    # Analyze directory without recursion
    ssf_tools utils file-info ./config --no-recurse
    ```
    """
    try:
        rich_output.info(f"Analyzing target: {target}")

        target_path = Path(target)

        # Check if target is an existing file or directory
        if target_path.exists():
            if target_path.is_file():
                # Single file case
                files = [target_path]
            else:
                # Directory case - discover all files
                recursive = not no_recurse
                files = file_discovery.discover_files_by_pattern(
                    base_path=target_path,
                    pattern="*",
                    recursive=recursive,
                )

                if not files:
                    rich_output.warning(
                        f"No files found in {target}",
                    )
                    return

                recurse_msg = "recursively" if recursive else "non-recursively"
                rich_output.info(
                    f"Found {len(files)} files {recurse_msg} in {target}",
                )
        else:
            # Target doesn't exist as-is, treat as a glob pattern
            # Extract directory and pattern components
            if "/" in target or "\\" in target:
                # Has path separators - split into directory and pattern
                parent_dir = target_path.parent
                pattern = target_path.name
                base_path = parent_dir if parent_dir.exists() else Path()
            else:
                # No path separators - pattern in current directory
                base_path = Path()
                pattern = target

            recursive = not no_recurse
            files = file_discovery.discover_files_by_pattern(
                base_path=base_path,
                pattern=pattern,
                recursive=recursive,
            )

            if not files:
                rich_output.warning(
                    f"No files found matching pattern '{pattern}' in {base_path}",
                )
                return

            recurse_msg = "recursively" if recursive else "non-recursively"
            rich_output.info(
                f"Found {len(files)} files matching '{pattern}' {recurse_msg} in {base_path}",
            )

        # Analyze each file and display results
        _display_file_analysis_table(files, file_processing, rich_output)

    except ValueError as e:
        rich_output.error(f"File discovery failed: {e}")
    except Exception as e:  # noqa: BLE001
        rich_output.error(f"Analysis failed: {e}")


def _display_file_analysis_table(
    files: list[Path],
    file_processing: FileProcessingService,
    rich_output: RichOutputService,
) -> None:
    """
    Display file analysis results in a rich table format.

    Args:
        files: List of file paths to analyze
        file_processing: File processing service for analysis
        rich_output: Rich output service for display

    """
    # Create table with file analysis columns
    table = Table(title="File Analysis Results")
    table.add_column("File", style="blue", no_wrap=False, max_width=40)
    table.add_column("MIME Type", style="cyan", max_width=25)
    table.add_column("Encoding", style="green", max_width=15)
    table.add_column("Language", style="yellow", max_width=15)
    table.add_column("Text", style="magenta", justify="center", max_width=6)
    table.add_column("Size", style="white", justify="right", max_width=10)

    # Analyze each file and add to table
    for file_path in files:
        # Initialize with default values
        mime_type = "Unknown"
        encoding = "Unknown"
        language = "Unknown"
        is_text = False
        size_display = "Unknown"

        # Try each detection method independently
        try:
            mime_type = file_processing.detect_mime_type(file_path) or "Unknown"
        except Exception as e:  # noqa: BLE001
            rich_output.warning(f"MIME detection failed for {file_path.name}: {e}")
            mime_type = "ERROR"

        try:
            encoding = file_processing.detect_encoding(file_path) or "Unknown"
        except Exception as e:  # noqa: BLE001
            rich_output.warning(f"Encoding detection failed for {file_path.name}: {e}")
            encoding = "ERROR"

        try:
            language = file_processing.detect_language(file_path) or "Unknown"
        except Exception as e:  # noqa: BLE001
            rich_output.warning(f"Language detection failed for {file_path.name}: {e}")
            language = "ERROR"

        try:
            is_text = file_processing.is_text_file(file_path)
        except Exception as e:  # noqa: BLE001
            rich_output.warning(f"Text detection failed for {file_path.name}: {e}")
            is_text = False

        # Get file size
        try:
            size_bytes = file_path.stat().st_size
            size_display = _format_file_size(size_bytes)
        except (OSError, PermissionError) as e:
            rich_output.warning(f"Size detection failed for {file_path.name}: {e}")
            size_display = "ERROR"

        # Truncate long values for better display
        display_mime_type = (
            mime_type[:20] + "..."
            if mime_type and len(mime_type) > 20  # noqa: PLR2004
            else mime_type
        )
        display_language = (
            language[:12] + "..."
            if language and len(language) > 12  # noqa: PLR2004
            else language
        )
        display_encoding = (
            encoding[:12] + "..."
            if encoding and len(encoding) > 12  # noqa: PLR2004
            else encoding
        )

        # Style text/binary indicator
        text_indicator = "✓" if is_text else "✗"
        text_style = "green" if is_text else "red"

        table.add_row(
            str(file_path.name),
            display_mime_type,
            display_encoding,
            display_language,
            f"[{text_style}]{text_indicator}[/{text_style}]",
            size_display,
        )

    # Display the table
    rich_output.console.print(table)

    # Summary information
    total_files = len(files)
    if total_files > 0:
        rich_output.info(f"Analysis complete. Processed {total_files} file(s).")


def _format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: File size in bytes

    Returns:
        Formatted size string (e.g., "1.2 KB", "3.4 MB")

    """
    if size_bytes == 0:
        return "0 B"

    size_units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    size = float(size_bytes)

    while size >= 1024.0 and unit_index < len(size_units) - 1:  # noqa: PLR2004
        size /= 1024.0
        unit_index += 1

    if unit_index == 0:
        return f"{int(size)} {size_units[unit_index]}"
    return f"{size:.1f} {size_units[unit_index]}"
