"""Core services container for dependency injection."""

from dependency_injector import containers, providers

from kp_ssf_tools.analyze.models import AnalysisConfiguration
from kp_ssf_tools.core.services.cache import CacheConfig, CacheService
from kp_ssf_tools.core.services.config import ConfigurationManager, ConfigurationService
from kp_ssf_tools.core.services.config.models import GlobalConfiguration
from kp_ssf_tools.core.services.excel_export import (
    DefaultColumnWidthAdjuster,
    DefaultDateFormatter,
    DefaultExcelFormatter,
    DefaultRowHeightAdjuster,
    DefaultSheetNameSanitizer,
    DefaultTableGenerator,
    DefaultTableStyler,
    DefaultTitleFormatter,
    DefaultWorkbookEngine,
    ExcelExportService,
)
from kp_ssf_tools.core.services.file_processing import (
    AutoMimeDetector,
    BinaryContentStreamer,
    CharsetNormalizerEncodingDetector,
    ConfigurableFileHashGenerator,
    FileDiscoveryService,
    FileProcessingService,
    HybridContentStreamer,
    PathUtilitiesService,
    PygmentsLanguageDetector,
)
from kp_ssf_tools.core.services.file_processing.validation import BasicFileValidator
from kp_ssf_tools.core.services.http_client import HttpClientService
from kp_ssf_tools.core.services.http_client.models import HttpConfig
from kp_ssf_tools.core.services.rich_output import RichOutputService
from kp_ssf_tools.core.services.timestamp import TimestampService


# Turn off Ruff auto-formatting as it's clobbering some of the longer lines in this container
# fmt: off
class CoreContainer(containers.DeclarativeContainer):
    """Container for core infrastructure services."""

    # Configuration injection
    config = providers.Configuration()

    # Core infrastructure services
    timestamp: providers.Singleton[
        TimestampService
    ] = providers.Singleton(
        TimestampService,
    )

    # Rich output service for beautiful terminal output
    rich_output: providers.Singleton[
        RichOutputService
    ] = providers.Singleton(
        RichOutputService,
        quiet=False,
        verbose=False,
        no_color=False,
    )

    # HTTP client configuration
    http_config: providers.Factory[
        HttpConfig
    ] = providers.Factory(
        HttpConfig,
        timeout_seconds=10.0,
        max_retries=3,
        user_agent="SSF-Tools/1.0",
        verify_ssl=True,
        cache_enabled=True,
    )

    # HTTP client service
    http_client: providers.Singleton[
        HttpClientService
    ] = providers.Singleton(
        HttpClientService,
        config=http_config,
        output=rich_output,
    )

    # File Processing Service Dependencies
    encoding_detector: providers.Singleton[
        CharsetNormalizerEncodingDetector
    ] = providers.Singleton(CharsetNormalizerEncodingDetector)

    mime_detector: providers.Singleton[
        AutoMimeDetector
    ] = providers.Singleton(AutoMimeDetector)

    language_detector: providers.Singleton[
        PygmentsLanguageDetector
    ] = providers.Singleton(PygmentsLanguageDetector)

    hash_generator: providers.Singleton[
        ConfigurableFileHashGenerator
    ] = providers.Singleton(ConfigurableFileHashGenerator)

    file_validator: providers.Singleton[
        BasicFileValidator
    ] = providers.Singleton(BasicFileValidator)

    file_discoverer: providers.Singleton[
        FileDiscoveryService
    ] = providers.Singleton(FileDiscoveryService)

    path_utilities: providers.Singleton[
        PathUtilitiesService
    ] = providers.Singleton(
        PathUtilitiesService,
        timestamp_service=timestamp,
    )

    # File Processing Service
    file_processing: providers.Singleton[
        FileProcessingService
    ] = providers.Singleton(
        FileProcessingService,
        encoding_detector=encoding_detector,
        hash_generator=hash_generator,
        file_validator=file_validator,
        file_discovery=file_discoverer,
        mime_detector=mime_detector,
        language_detector=language_detector,
        rich_output=rich_output,
    )

    # Binary Content Streaming Services for entropy analysis
    binary_content_streamer: providers.Factory[
        BinaryContentStreamer
    ] = providers.Factory(BinaryContentStreamer)

    hybrid_content_streamer: providers.Factory[
        HybridContentStreamer
    ] = providers.Factory(HybridContentStreamer)

    # Configuration services for unified ssf-tools-config.yaml file sections
    global_config_service: providers.Singleton[
        ConfigurationService[GlobalConfiguration]
    ] = providers.Singleton(
        ConfigurationService,
        config_model=GlobalConfiguration,
        rich_output=rich_output,
        timestamp_service=timestamp,
        config_section="global",
    )

    entropy_config_service: providers.Singleton[
        ConfigurationService[AnalysisConfiguration]
    ] = providers.Singleton(
        ConfigurationService,
        config_model=AnalysisConfiguration,
        rich_output=rich_output,
        timestamp_service=timestamp,
        config_section="entropy",
    )

    # Configuration manager for unified config file approach
    config_manager: providers.Singleton[
        ConfigurationManager
    ] = providers.Singleton(ConfigurationManager)

    # Cache service configuration
    cache_config: providers.Factory[
        CacheConfig
    ] = providers.Factory(CacheConfig)

    # Unified cache service
    cache: providers.Singleton[
        CacheService
    ] = providers.Singleton(
        CacheService,
        config=cache_config,
        output=rich_output,
    )

    # Excel export services
    sheet_name_sanitizer: providers.Singleton[
        DefaultSheetNameSanitizer
    ] = providers.Singleton(DefaultSheetNameSanitizer)

    column_width_adjuster: providers.Singleton[
        DefaultColumnWidthAdjuster
    ] = providers.Singleton(
        DefaultColumnWidthAdjuster,
        sheet_name_sanitizer=sheet_name_sanitizer,
        )

    date_formatter: providers.Singleton[
        DefaultDateFormatter
    ] = providers.Singleton(DefaultDateFormatter)

    row_height_adjuster: providers.Singleton[
        DefaultRowHeightAdjuster
    ] = providers.Singleton(DefaultRowHeightAdjuster)

    excel_formatter: providers.Singleton[
        DefaultExcelFormatter
    ] = providers.Singleton(
        DefaultExcelFormatter,
        column_width_adjuster=column_width_adjuster,
    )

    table_styler: providers.Singleton[
        DefaultTableStyler
    ] = providers.Singleton(DefaultTableStyler)

    title_formatter: providers.Singleton[
        DefaultTitleFormatter
    ] = providers.Singleton(DefaultTitleFormatter)

    workbook_engine: providers.Singleton[
        DefaultWorkbookEngine
    ] = providers.Singleton(DefaultWorkbookEngine)

    table_generator: providers.Singleton[
        DefaultTableGenerator
    ] = providers.Singleton(
        DefaultTableGenerator,
        formatter=excel_formatter,
        date_formatter=date_formatter,
        column_width_adjuster=column_width_adjuster,
        row_height_adjuster=row_height_adjuster,
        table_styler=table_styler,
    )

    excel_export_service: providers.Singleton[
        ExcelExportService
    ] = providers.Singleton(
        ExcelExportService,
        sheet_name_sanitizer=sheet_name_sanitizer,
        column_width_adjuster=column_width_adjuster,
        date_formatter=date_formatter,
        row_height_adjuster=row_height_adjuster,
        excel_formatter=excel_formatter,
        table_generator=table_generator,
        title_formatter=title_formatter,
        workbook_engine=workbook_engine,
    )
