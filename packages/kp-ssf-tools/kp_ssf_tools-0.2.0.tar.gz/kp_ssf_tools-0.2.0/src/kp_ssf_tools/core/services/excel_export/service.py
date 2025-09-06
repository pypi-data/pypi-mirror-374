"""Service definition for dependency-injector implementation of Excel export functionality."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    import pandas as pd
    from openpyxl.worksheet.worksheet import Worksheet

    from kp_ssf_tools.core.services.excel_export.interfaces import (
        ColumnWidthAdjusterProtocol,
        DateFormatterProtocol,
        ExcelFormatterProtocol,
        RowHeightAdjusterProtocol,
        SheetNameSanitizerProtocol,
        TableGeneratorProtocol,
        TitleFormatterProtocol,
        WorkbookEngineProtocol,
    )


class ExcelExportService:
    """Service for all Excel export operations."""

    def __init__(  # noqa: PLR0913
        self,
        sheet_name_sanitizer: SheetNameSanitizerProtocol,
        column_width_adjuster: ColumnWidthAdjusterProtocol,
        date_formatter: DateFormatterProtocol,
        row_height_adjuster: RowHeightAdjusterProtocol,
        excel_formatter: ExcelFormatterProtocol,
        table_generator: TableGeneratorProtocol,
        title_formatter: TitleFormatterProtocol,
        workbook_engine: WorkbookEngineProtocol,
    ) -> None:
        """
        Initialize the Excel export service.

        Args:
            sheet_name_sanitizer: Service for sanitizing and validating sheet names
            column_width_adjuster: Service for adjusting column widths
            date_formatter: Service for formatting date columns
            row_height_adjuster: Service for adjusting row heights
            excel_formatter: Service for table alignment and formatting
            table_generator: Service for creating and styling Excel tables
            title_formatter: Service for formatting title cells
            workbook_engine: Service for creating Excel writers and managing output

        """
        self.sheet_name_sanitizer: SheetNameSanitizerProtocol = sheet_name_sanitizer
        self.column_width_adjuster: ColumnWidthAdjusterProtocol = column_width_adjuster
        self.date_formatter: DateFormatterProtocol = date_formatter
        self.row_height_adjuster: RowHeightAdjusterProtocol = row_height_adjuster
        self.excel_formatter: ExcelFormatterProtocol = excel_formatter
        self.table_generator: TableGeneratorProtocol = table_generator
        self.title_formatter: TitleFormatterProtocol = title_formatter
        self.workbook_engine: WorkbookEngineProtocol = workbook_engine

    def export_dataframe_to_excel(
        self,
        data_frame: pd.DataFrame,
        output_path: Path,
        sheet_name: str = "Sheet1",
        title: str | None = None,
        *,
        as_table: bool = True,
    ) -> None:
        """
        Export a DataFrame to an Excel file with formatting and optional table styling.

        Args:
            data_frame: The DataFrame to export
            output_path: Path to the output Excel file
            sheet_name: Name of the worksheet (default: "Sheet1")
            title: Optional title to add to the worksheet
            as_table: Whether to format the data as an Excel table (default: True)

        """
        sanitized_sheet_name: str = self.sheet_name_sanitizer.sanitize_sheet_name(
            sheet_name,
        )
        with self.workbook_engine.create_writer(output_path) as writer:
            data_frame.to_excel(
                writer,
                sheet_name=sanitized_sheet_name,
                index=False,
                startrow=1 if title else 0,
            )
            worksheet: Worksheet = writer.sheets[sanitized_sheet_name]

            if title:
                self.title_formatter.apply_title_format(worksheet, title, row=1, col=1)

            if as_table:
                self.table_generator.format_as_excel_table(
                    worksheet,
                    data_frame,
                    startrow=2 if title else 1,
                )
            else:
                # Only apply basic formatting without table styling
                self.column_width_adjuster.auto_adjust_column_widths(
                    worksheet,
                    data_frame,
                )
                self.date_formatter.format_date_columns(
                    worksheet,
                    data_frame,
                    startrow=2 if title else 1,
                )
                self.row_height_adjuster.adjust_row_heights(
                    worksheet,
                    data_frame,
                    startrow=2 if title else 1,
                )
