"""File processing service for encoding detection, validation, and hashing."""

from kp_ssf_tools.core.services.file_processing.binary_streaming import (
    BinaryContentStreamer,
    HybridContentStreamer,
)
from kp_ssf_tools.core.services.file_processing.discovery import (
    FileDiscoveryService,
)
from kp_ssf_tools.core.services.file_processing.encoding import (
    CharsetNormalizerEncodingDetector,
    RobustEncodingDetector,
)
from kp_ssf_tools.core.services.file_processing.hashing import (
    ConfigurableFileHashGenerator,
    SHA384FileHashGenerator,
)
from kp_ssf_tools.core.services.file_processing.interfaces import (
    BinaryStreamerProtocol,
    ContentStreamer,
    EncodingDetector,
    FileDiscoverer,
    FileValidator,
    HashGenerator,
    MimeTypeDetector,
    PathUtilities,
)
from kp_ssf_tools.core.services.file_processing.language_detection import (
    PygmentsLanguageDetector,
)
from kp_ssf_tools.core.services.file_processing.mime_detection import (
    AutoMimeDetector,
    LibmagicMimeDetector,
    PureMagicMimeDetector,
)
from kp_ssf_tools.core.services.file_processing.path_utilities import (
    PathUtilitiesService,
)
from kp_ssf_tools.core.services.file_processing.service import (
    FileProcessingService,
)
from kp_ssf_tools.core.services.file_processing.streaming import (
    FileContentStreamer,
)
from kp_ssf_tools.core.services.file_processing.validation import (
    BasicFileValidator,
)

__all__: list[str] = [
    "AutoMimeDetector",
    "BasicFileValidator",
    "BinaryContentStreamer",
    "BinaryStreamerProtocol",
    "CharsetNormalizerEncodingDetector",
    "ConfigurableFileHashGenerator",
    "ContentStreamer",
    "EncodingDetector",
    "FileContentStreamer",
    "FileDiscoverer",
    "FileDiscoveryService",
    "FileProcessingService",
    "FileValidator",
    "HashGenerator",
    "HybridContentStreamer",
    "LibmagicMimeDetector",
    "MimeTypeDetector",
    "PathUtilities",
    "PathUtilitiesService",
    "PureMagicMimeDetector",
    "PygmentsLanguageDetector",
    "RobustEncodingDetector",
    "SHA384FileHashGenerator",
]
