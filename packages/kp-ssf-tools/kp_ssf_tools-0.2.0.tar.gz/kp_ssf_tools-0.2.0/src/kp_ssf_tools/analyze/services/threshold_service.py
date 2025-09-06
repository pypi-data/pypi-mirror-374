"""Threshold provider for Content Aware Thresholding."""

from __future__ import annotations

from typing import TYPE_CHECKING

from kp_ssf_tools.analyze.models.content_aware import ContentAwareThresholds
from kp_ssf_tools.analyze.models.types import EntropyLevel

if TYPE_CHECKING:
    from kp_ssf_tools.analyze.models.types import FileType

__all__ = [
    "ContentAwareThresholdManager",
    "ContentAwareThresholds",
]


class ContentAwareThresholdManager:
    """
    Manages content-aware thresholds for different file types.

    Concrete implementation of the ThresholdProviderProtocol.
    """

    def __init__(self) -> None:
        # Cache pre-built models to avoid repeated conversions
        self.threshold_cache: dict[FileType, ContentAwareThresholds] = (
            ContentAwareThresholds.get_default_models()
        )

    def get_thresholds(self, file_type: FileType) -> ContentAwareThresholds:
        if file_type in self.threshold_cache:
            return self.threshold_cache[file_type]

        # Use factory method for unknown types
        return ContentAwareThresholds.for_file_type(file_type)

    def classify_entropy_level(
        self,
        entropy: float,
        file_type: FileType,
    ) -> EntropyLevel:
        """
        Classify entropy level based on content-aware thresholds.

        Args:
            entropy: Shannon entropy value
            file_type: The detected file type

        Returns:
            Entropy level classification enum

        """
        thresholds: ContentAwareThresholds = self.get_thresholds(file_type)

        if entropy <= thresholds.very_low_threshold:
            return EntropyLevel.VERY_LOW
        if entropy <= thresholds.low_threshold:
            return EntropyLevel.LOW
        if entropy <= thresholds.medium_threshold:
            return EntropyLevel.MEDIUM
        if entropy <= thresholds.medium_high_threshold:
            return EntropyLevel.MEDIUM_HIGH
        if entropy <= thresholds.high_threshold:
            return EntropyLevel.HIGH

        # If not any of the others, then it has to be CRITICAL
        return EntropyLevel.CRITICAL


if __name__ == "__main__":
    print("Content-Aware Threshold Manager")
