"""Cache service protocol definitions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from datetime import timedelta
    from pathlib import Path

    from kp_ssf_tools.core.services.cache.models import (
        CacheCategory,
        CacheInfo,
        CategoryConfig,
    )


class CacheServiceProtocol(Protocol):
    """Protocol for unified cache management across SSF Tools."""

    def get_cache_info(self) -> CacheInfo:
        """
        Get comprehensive cache statistics and information.

        Returns:
            CacheInfo: An object containing cache statistics and metadata.

        """

    def clear_cache(self, category: CacheCategory | None = None) -> int:
        """
        Clear cache by category or all. Returns items cleared.

        Args:
            category (CacheCategory | None): The cache category to clear.
                If None, clears all cache entries.

        Returns:
            int: The number of cache items cleared.

        """

    def get_cache_size(self, category: CacheCategory | None = None) -> int:
        """
        Get cache size in bytes.

        Args:
            category (CacheCategory | None): The cache category to get size for.
                If None, returns the total cache size.

        Returns:
            int: The size of the cache in bytes.

        """

    def cleanup_expired(self, max_age: timedelta | None = None) -> int:
        """
        Remove expired cache entries. Returns items removed.

        Args:
            max_age (timedelta | None): If specified, only remove entries older than this age.

        Returns:
            int: The number of cache items removed.

        """

    def list_cache_categories(self) -> list[CacheCategory]:
        """
        List available cache categories.

        Returns:
            list[CacheCategory]: A list of available cache categories.

        """

    def get_cache_path(self, category: CacheCategory) -> Path:
        """
        Get the cache directory path for a category.

        Args:
            category (CacheCategory): The cache category to get the path for.

        Returns:
            Path: The path to the cache directory for the specified category.

        """

    def is_cache_enabled(self, category: CacheCategory) -> bool:
        """
        Check if caching is enabled for a category.

        Args:
            category (CacheCategory): The cache category to check.

        Returns:
            bool: True if caching is enabled for the category, False otherwise.

        """

    def get_category_config(self, category: CacheCategory) -> CategoryConfig:
        """
        Get configuration for a specific cache category.

        Args:
            category (CacheCategory): The cache category to get the configuration for.

        Returns:
            CategoryConfig: The configuration object for the specified category.

        """
