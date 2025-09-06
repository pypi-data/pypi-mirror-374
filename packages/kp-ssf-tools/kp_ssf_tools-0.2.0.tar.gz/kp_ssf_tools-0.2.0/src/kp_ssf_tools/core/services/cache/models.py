"""Cache service models and configuration."""

from __future__ import annotations

from datetime import datetime  # noqa: TC003
from enum import StrEnum
from pathlib import Path
from typing import ClassVar

from pydantic import Field, field_validator

from kp_ssf_tools.models.base import SSFToolsBaseModel


class CacheCategory(StrEnum):
    """
    Standard cache categories across SSF Tools.

    HTTP_RESPONSES and WORDLISTS are currently implemented.
    """

    HTTP_RESPONSES = "http_responses"
    WORDLISTS = "wordlists"
    # Future categories (not implemented yet):
    # FILE_HASHES = "file_hashes"
    # ENCODING_DETECTION = "encoding_detection"
    # MIME_DETECTION = "mime_detection"
    # ENTROPY_THRESHOLDS = "entropy_thresholds"
    # TIMESTAMP_FILENAMES = "timestamp_filenames"
    # VOLATILITY_PROFILES = "volatility_profiles"


class CategoryConfig(SSFToolsBaseModel):
    """Configuration for a specific cache category."""

    enabled: bool = True
    ttl_hours: int = 168  # 1 week default (as per MVP requirements)
    max_size_mb: int = 100
    cleanup_threshold: float = 0.8  # Cleanup when 80% full

    @field_validator("ttl_hours")
    @classmethod
    def validate_ttl_hours(cls, v: int) -> int:
        """Validate TTL hours is positive."""
        if v <= 0:
            msg = "TTL hours must be positive"
            raise ValueError(msg)
        return v

    @field_validator("max_size_mb")
    @classmethod
    def validate_max_size_mb(cls, v: int) -> int:
        """Validate max size is positive."""
        if v <= 0:
            msg = "Max size must be positive"
            raise ValueError(msg)
        return v

    @field_validator("cleanup_threshold")
    @classmethod
    def validate_cleanup_threshold(cls, v: float) -> float:
        """Validate cleanup threshold is between 0 and 1."""
        if not 0 < v <= 1:
            msg = "Cleanup threshold must be between 0 and 1"
            raise ValueError(msg)
        return v


class CategoryInfo(SSFToolsBaseModel):
    """Information about a specific cache category."""

    size_bytes: int = Field(ge=0, description="Size in bytes")
    item_count: int = Field(ge=0, description="Number of items")
    oldest_item: datetime | None = Field(
        default=None,
        description="Oldest item timestamp",
    )
    newest_item: datetime | None = Field(
        default=None,
        description="Newest item timestamp",
    )
    ttl_hours: int = Field(gt=0, description="Time to live in hours")


class CacheInfo(SSFToolsBaseModel):
    """Cache information and statistics."""

    total_size_bytes: int = Field(ge=0, description="Total cache size in bytes")
    total_items: int = Field(ge=0, description="Total number of items")
    categories: dict[str, CategoryInfo] = Field(
        default_factory=dict,
        description="Information by category",
    )
    base_cache_dir: Path = Field(description="Base cache directory path")
    last_cleanup: datetime | None = Field(
        default=None,
        description="Last cleanup timestamp",
    )


class CacheConfig(SSFToolsBaseModel):
    """Cache service configuration."""

    # Using platformdirs default for cache directory (MVP requirement)
    base_cache_dir: Path | None = Field(
        default=None,
        description="Base cache directory (None for platformdirs default)",
    )
    max_total_size_mb: int = Field(
        default=1024,
        gt=0,
        description="Total cache size limit",
    )
    default_ttl_hours: int = Field(
        default=168,
        gt=0,
        description="Default TTL (1 week)",
    )
    cleanup_interval_hours: int = Field(
        default=24,
        gt=0,
        description="Auto-cleanup frequency",
    )
    categories: dict[CacheCategory, CategoryConfig] = Field(
        default_factory=dict,
        description="Category-specific configurations",
    )

    # Default configurations for supported cache categories
    DEFAULT_CATEGORY_CONFIGS: ClassVar[dict[CacheCategory, CategoryConfig]] = {
        CacheCategory.HTTP_RESPONSES: CategoryConfig(
            enabled=True,
            ttl_hours=168,  # 1 week as per MVP requirements
            max_size_mb=100,
            cleanup_threshold=0.8,
        ),
        CacheCategory.WORDLISTS: CategoryConfig(
            enabled=True,
            ttl_hours=336,  # 2 weeks - wordlists change less frequently
            max_size_mb=500,  # Larger cache for wordlists
            cleanup_threshold=0.8,
        ),
        # Future categories can be added here:
        # CacheCategory.FILE_HASHES: CategoryConfig(
        #     enabled=True,
        #     ttl_hours=168,  # 1 week
        #     max_size_mb=50,
        #     cleanup_threshold=0.8,
        # ),
    }

    def get_category_config(self, category: CacheCategory) -> CategoryConfig:
        """Get configuration for a specific category with fallback to defaults."""
        if category in self.categories:
            return self.categories[category]

        # Check if category has a default configuration
        if category in self.DEFAULT_CATEGORY_CONFIGS:
            return self.DEFAULT_CATEGORY_CONFIGS[category]

        # Fallback for unsupported categories
        msg = f"Unsupported cache category: {category}"
        raise ValueError(msg)

    def get_supported_categories(self) -> list[CacheCategory]:
        """Get list of supported cache categories."""
        return list(self.DEFAULT_CATEGORY_CONFIGS.keys())

    def get_cache_dir(self) -> Path:
        """Get the actual cache directory, using platformdirs if None."""
        if self.base_cache_dir is not None:
            return self.base_cache_dir.expanduser().resolve()

        # Use platformdirs for OS-specific cache directory (MVP requirement)
        from platformdirs import user_cache_dir

        cache_dir = Path(user_cache_dir("ssf_tools", "KirkpatrickPrice"))
        return cache_dir.resolve()


# Rebuild models after all forward references are resolved
CategoryInfo.model_rebuild()
CacheInfo.model_rebuild()
CacheConfig.model_rebuild()
