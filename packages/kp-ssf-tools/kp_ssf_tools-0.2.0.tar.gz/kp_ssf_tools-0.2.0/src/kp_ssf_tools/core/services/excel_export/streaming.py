"""
Streaming Excel exporter for entropy analysis with minimal memory usage.

Moved from analyze.services to core.services.excel_export.
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any, Self

import pandas as pd
import xlsxwriter

from kp_ssf_tools.analyze.models.types import EntropyLevel

if TYPE_CHECKING:
    import types
    from collections.abc import Generator

    from kp_ssf_tools.analyze.services.entropy import EntropyAnalyzer


class StreamingWorkbookEngine:
    """
    Streaming workbook engine for Excel export with constant memory usage.

    Uses xlsxwriter with constant_memory mode for efficient streaming of large datasets.
    """

    def __init__(self) -> None:
        self._writer = None
        self._workbook = None

    @contextmanager
    def create_streaming_writer(
        self,
        output_path: Path,
        options: dict[str, Any] | None = None,
    ) -> Generator[pd.ExcelWriter]:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        writer_options = {"constant_memory": True}
        if options:
            writer_options.update(options)
        writer = pd.ExcelWriter(
            output_path,
            engine="xlsxwriter",
            engine_kwargs={"options": writer_options},
        )
        try:
            yield writer
        finally:
            writer.close()


class StreamingExcelExporter:
    """
    Stream analysis results directly to Excel with minimal RAM usage.

    Uses dependency injection to leverage existing Excel export services while adding streaming capabilities for large datasets.
    """

    MAX_ROWS = 1_048_576
    MAX_WORKSHEETS = 255
    WARNING_THRESHOLD = 900_000

    def __init__(
        self,
        output_path: Path,
        risk_threshold: EntropyLevel | str = EntropyLevel.MEDIUM_HIGH,
        services: dict | None = None,
    ) -> None:
        self.workbook = xlsxwriter.Workbook(str(output_path), {"constant_memory": True})
        # Defensive conversion: always store risk_threshold as EntropyLevel
        if isinstance(risk_threshold, str):
            risk_threshold = EntropyLevel(risk_threshold)
        self.risk_threshold = risk_threshold
        self.output_path = output_path
        self.services = services or {}
        self.sheet_name_sanitizer = self.services.get("sheet_name_sanitizer")
        self.title_formatter = self.services.get("title_formatter")
        self.workbook_engine = self.services.get("workbook_engine")
        self.rich_output = self.services.get("rich_output")
        self._setup_summary_worksheet()
        self.worksheet_names = {}
        self.worksheets = {}
        self.used_names = set()
        self.summary_row = 1
        self.total_regions_written = 0
        self.warned_about_limit = False
        self.data_sample_format = self.workbook.add_format(
            {
                "font_name": "Consolas",
                "font_size": 10,
            },
        )
        self.data_sample_format_fallback = self.workbook.add_format(
            {
                "font_name": "Courier New",
                "font_size": 10,
            },
        )

    def warn_if_too_many_files(self, file_count: int) -> None:
        if file_count > self.MAX_WORKSHEETS - 1 and not self.warned_about_limit:
            if self.rich_output:
                self.rich_output.warning(
                    f"Excel worksheet limit: {file_count} files found. Only {self.MAX_WORKSHEETS} worksheets allowed (including summary).",
                )
            self.warned_about_limit = True

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        self.close()

    def _get_unique_worksheet_name(self, base_name: str) -> str:
        # Excel worksheet names max 31 chars, sanitize and deduplicate
        name = base_name[:28]
        suffix = 1
        candidate = name
        while candidate in self.used_names:
            candidate = f"{name}_{suffix:02d}"
            suffix += 1
        self.used_names.add(candidate)
        return candidate

    def _setup_file_worksheet(
        self,
        file_path: Path,
    ) -> tuple[str, xlsxwriter.workbook.Worksheet]:
        base_name = file_path.name.replace("/", "_").replace("\\", "_")
        ws_name = self._get_unique_worksheet_name(base_name)
        ws = self.workbook.add_worksheet(ws_name)
        # Row 0: full file path
        ws.write(0, 0, str(file_path))
        # Row 2: column headers
        headers = [
            "Offset",
            "Size",
            "Entropy",
            "Level",
            "Confidence",
            "Data Sample",
        ]
        for col, header in enumerate(headers):
            ws.write(2, col, header, self.header_format)
        ws.set_column("A:F", 15)
        return ws_name, ws

    def process_file_streaming(  # noqa: PLR0913
        self,
        file_path: Path,
        analyzer: EntropyAnalyzer,
        *,
        file_chunk_size: int = 65536,
        analysis_block_size: int = 64,
        step_size: int = 16,
        include_samples: bool = False,
    ) -> tuple[int, int]:
        """
        Stream entropy analysis results for a file and write to Excel.

        Args:
            file_path: Path to file to analyze
            analyzer: EntropyAnalyzer instance
            file_chunk_size: Size of file I/O chunks in bytes
            analysis_block_size: Size of analysis blocks in bytes
            step_size: Step size for sliding window
            include_samples: Whether to include data samples in the output

        Returns:
            Tuple of (total_regions, high_risk_regions)

        """
        total_regions = 0
        high_risk_regions = 0
        # Setup per-file worksheet
        ws_name, ws = self._setup_file_worksheet(file_path)
        self.worksheet_names[str(file_path)] = ws_name
        file_row = 3  # Start writing data at row 3
        for result in analyzer.analyze_file_generator(
            file_path,
            min_risk_level=self.risk_threshold,
            file_chunk_size=file_chunk_size,
            analysis_block_size=analysis_block_size,
            step_size=step_size,
            include_samples=include_samples,
        ):
            if result.type == "region":
                data = result.data
                ws.write(file_row, 0, data.get("offset", 0))
                ws.write(file_row, 1, data.get("size", 0))
                ws.write(file_row, 2, data.get("entropy", 0.0))
                ws.write(file_row, 3, data.get("level", ""))
                ws.write(file_row, 4, data.get("confidence", 0.0))
                if include_samples:
                    sample_bytes = data.get("data_sample", b"")
                else:
                    sample_bytes = b"Use `--include-samples` to include data samples"
                # Always sanitize and truncate the sample string to avoid Excel corruption
                safe_sample = self.format_data_sample(sample_bytes)[:64]
                # Remove any leading '=' to avoid Excel formula injection
                if safe_sample.startswith("="):
                    safe_sample = "'" + safe_sample
                try:
                    ws.write(
                        file_row,
                        5,
                        safe_sample,
                        self.data_sample_format,
                    )
                except Exception:  # noqa: BLE001
                    ws.write(
                        file_row,
                        5,
                        safe_sample,
                        self.data_sample_format_fallback,
                    )
                file_row += 1
                total_regions += 1
                high_risk_regions += 1
            elif result.type == "summary":
                # Write summary to summary sheet, include worksheet cross-ref
                row = self.summary_row
                self.summary_sheet.write(row, 0, str(file_path))
                self.summary_sheet.write(row, 1, file_path.name)
                # Add hyperlink to worksheet name in summary
                worksheet_link = f"internal:'{ws_name}'!A1"
                self.summary_sheet.write_url(row, 2, worksheet_link, string=ws_name)
                self.summary_sheet.write(
                    row,
                    3,
                    result.data.get("file_size", 0) / 1024 / 1024,
                )
                self.summary_sheet.write(
                    row,
                    4,
                    result.data.get("overall_entropy", 0.0),
                )
                self.summary_sheet.write(row, 5, result.data.get("total_regions", 0))
                self.summary_sheet.write(
                    row,
                    6,
                    result.data.get("high_risk_regions", 0),
                )
                self.summary_sheet.write(row, 7, self.risk_threshold.value)
                self.summary_sheet.write(
                    row,
                    8,
                    result.data.get("processing_time", 0.0),
                )
                self.summary_sheet.write(row, 9, result.data.get("mime_type", ""))
                self.summary_sheet.write(row, 10, result.data.get("language", ""))
                self.summary_row += 1
        return total_regions, high_risk_regions

    def format_data_sample(self, data: bytes | str) -> str:
        """Convert bytes or str to a readable string: printable chars or hex."""
        ascii_printable: set[int] = set(range(32, 127))  # Printable ASCII range

        if isinstance(data, str):
            # Already a string, return as-is
            return data
        result: list[str] = [
            chr(b) if isinstance(b, int) and b in ascii_printable else f"\\x{b:02x}"
            for b in data
        ]
        return "".join(result)

    def _setup_summary_worksheet(self) -> None:
        self.summary_sheet = self.workbook.add_worksheet("File Summary")
        self.header_format = self.workbook.add_format(
            {
                "bold": True,
                "bg_color": "#4472C4",
                "font_color": "white",
                "border": 1,
            },
        )
        self.high_risk_format = self.workbook.add_format(
            {
                "bg_color": "#FFC7CE",
                "font_color": "#9C0006",
            },
        )
        self.medium_risk_format = self.workbook.add_format(
            {
                "bg_color": "#FFEB9C",
                "font_color": "#9C6500",
            },
        )
        self.low_risk_format = self.workbook.add_format(
            {
                "bg_color": "#C6EFCE",
                "font_color": "#006100",
            },
        )
        headers = [
            "File Path",
            "File Name",
            "Worksheet Name",
            "File Size (MB)",
            "Overall Entropy",
            "Total Regions Analyzed",
            "High Risk Regions",
            "Risk Level",
            "Processing Time (s)",
            "MIME Type",
            "Language",
        ]
        for col, header in enumerate(headers):
            self.summary_sheet.write(0, col, header, self.header_format)
        self.summary_sheet.set_column("A:A", 50)
        self.summary_sheet.set_column("B:B", 30)
        self.summary_sheet.set_column("C:K", 15)

    def _setup_regions_worksheet(self) -> None:
        self.regions_sheet = self.workbook.add_worksheet("Regions")
        headers = [
            "File Path",
            "Offset",
            "Size",
            "Entropy",
            "Level",
            "Confidence",
            "Data Sample",
        ]
        for col, header in enumerate(headers):
            self.regions_sheet.write(0, col, header, self.header_format)

    def close(self) -> None:
        self.workbook.close()
