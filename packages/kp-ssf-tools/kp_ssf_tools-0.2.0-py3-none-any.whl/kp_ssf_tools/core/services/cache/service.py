"""Cache service implementation."""

from __future__ import annotations

import shutil
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from kp_ssf_tools.core.services.cache.models import (
    CacheCategory,
    CacheConfig,
    CacheInfo,
    CategoryInfo,
)

if TYPE_CHECKING:
    from pathlib import Path

    from kp_ssf_tools.core.services.cache.models import CategoryConfig
    from kp_ssf_tools.core.services.rich_output.interfaces import RichOutputProtocol


class CacheService:
    """
    Unified cache service implementation.

    For MVP, this only implements HTTP_RESPONSES category support.
    """

    def __init__(
        self,
        config: CacheConfig,
        output: RichOutputProtocol,
    ) -> None:
        """
        Initialize cache service with configuration and output handler.

        Args:
            config (CacheConfig): The cache configuration object.
            output (RichOutputProtocol): The output handler for logging and user feedback.

        """
        self._config = config
        self._output = output
        self._ensure_cache_directories()

    def _ensure_cache_directories(self) -> None:
        """Create cache directories for supported categories."""
        for category in self._config.get_supported_categories():
            cache_path = self.get_cache_path(category)
            cache_path.mkdir(parents=True, exist_ok=True)

    def get_cache_path(self, category: CacheCategory) -> Path:
        """
        Get the cache directory path for a category.

        Args:
            category (CacheCategory): The cache category to get the path for.

        Returns:
            Path: The path to the cache directory for the specified category.

        """
        base_dir = self._config.get_cache_dir()
        return base_dir / category.value

    def get_cache_info(self) -> CacheInfo:
        """
        Get comprehensive cache statistics and information.

        Returns:
            CacheInfo: An object containing cache statistics and metadata.

        """
        categories = {}
        total_size = 0
        total_items = 0

        # Process all supported categories
        for category in self._config.get_supported_categories():
            category_info = self._get_category_info(category)
            categories[category.value] = category_info
            total_size += category_info.size_bytes
            total_items += category_info.item_count

        return CacheInfo(
            total_size_bytes=total_size,
            total_items=total_items,
            categories=categories,
            base_cache_dir=self._config.get_cache_dir(),
            last_cleanup=self._get_last_cleanup_time(),
        )

    def _get_category_info(self, category: CacheCategory) -> CategoryInfo:
        """
        Get information about a specific cache category.

        Args:
            category (CacheCategory): The cache category to retrieve information for.

        Returns:
            CategoryInfo: An object containing information about the cache category.

        """
        cache_path = self.get_cache_path(category)

        if not cache_path.exists():
            config = self._config.get_category_config(category)
            return CategoryInfo(
                size_bytes=0,
                item_count=0,
                oldest_item=None,
                newest_item=None,
                ttl_hours=config.ttl_hours,
            )

        # Calculate directory size and file count
        total_size = 0
        file_count = 0
        oldest_time: datetime | None = None
        newest_time: datetime | None = None

        for file_path in cache_path.rglob("*"):
            if file_path.is_file():
                file_count += 1
                stat = file_path.stat()
                total_size += stat.st_size

                mtime = datetime.fromtimestamp(stat.st_mtime, tz=UTC)
                if oldest_time is None or mtime < oldest_time:
                    oldest_time = mtime
                if newest_time is None or mtime > newest_time:
                    newest_time = mtime

        config = self._config.get_category_config(category)
        return CategoryInfo(
            size_bytes=total_size,
            item_count=file_count,
            oldest_item=oldest_time,
            newest_item=newest_time,
            ttl_hours=config.ttl_hours,
        )

    def _get_last_cleanup_time(self) -> datetime | None:
        """Get the last cleanup time from marker file."""
        cleanup_marker = self._config.get_cache_dir() / ".last_cleanup"
        if cleanup_marker.exists():
            return datetime.fromtimestamp(cleanup_marker.stat().st_mtime, tz=UTC)
        return None

    def _set_last_cleanup_time(self) -> None:
        """Update the last cleanup time marker file."""
        cleanup_marker = self._config.get_cache_dir() / ".last_cleanup"
        cleanup_marker.touch()

    def clear_cache(self, category: CacheCategory | None = None) -> int:
        """
        Clear cache by category or all. Returns items cleared.

        Args:
            category (CacheCategory | None): The cache category to clear.
                If None, clears all cache entries.

        Returns:
            int: The number of cache items cleared.

        """
        if category is None:
            # Clear all supported categories
            total_cleared = 0
            for supported_category in self._config.get_supported_categories():
                total_cleared += self.clear_cache(supported_category)
            return total_cleared

        # For MVP, only support HTTP_RESPONSES
        if category not in self.list_cache_categories():
            msg = f"Category {category.value} not supported"
            self._output.warning(msg)
            return 0

        cache_path = self.get_cache_path(category)
        if not cache_path.exists():
            return 0

        # Count files before deletion
        file_count = sum(
            1 for file_path in cache_path.rglob("*") if file_path.is_file()
        )

        # Remove the entire category directory
        shutil.rmtree(cache_path)

        # Recreate the empty directory
        cache_path.mkdir(parents=True, exist_ok=True)

        self._set_last_cleanup_time()
        return file_count

    def get_cache_size(self, category: CacheCategory | None = None) -> int:
        """
        Get cache size in bytes.

        Args:
            category (CacheCategory | None): The cache category to get size for.
                If None, returns the total cache size.

        Returns:
            int: The size of the cache in bytes.

        """
        if category is None:
            # Get total size across all supported categories
            total_size = 0
            for supported_category in self._config.get_supported_categories():
                total_size += self.get_cache_size(supported_category)
            return total_size

        # Check if category is supported
        if category not in self.list_cache_categories():
            return 0

        cache_path = self.get_cache_path(category)
        if not cache_path.exists():
            return 0

        total_size = 0
        for file_path in cache_path.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size

        return total_size

    def cleanup_expired(self, max_age: timedelta | None = None) -> int:
        """
        Remove expired cache entries. Returns items removed.

        Args:
            max_age (timedelta | None): If specified, only remove entries older than this age.

        Returns:
            int: The number of cache items removed.

        """
        if max_age is None:
            # Use default TTL from config
            config = self._config.get_category_config(CacheCategory.HTTP_RESPONSES)
            max_age = timedelta(hours=config.ttl_hours)

        cutoff_time = datetime.now(tz=UTC) - max_age
        removed_count = 0

        # For MVP, only process HTTP_RESPONSES category
        cache_path = self.get_cache_path(CacheCategory.HTTP_RESPONSES)
        if not cache_path.exists():
            return 0

        for file_path in cache_path.rglob("*"):
            if file_path.is_file():
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime, tz=UTC)
                if mtime < cutoff_time:
                    try:
                        file_path.unlink()
                        removed_count += 1
                    except OSError:
                        # File might have been removed by another process
                        pass

        self._set_last_cleanup_time()
        return removed_count

    def list_cache_categories(self) -> list[CacheCategory]:
        """
        List available cache categories.

        Returns:
            list[CacheCategory]: A list of available cache categories.

        """
        return self._config.get_supported_categories()

    def is_cache_enabled(self, category: CacheCategory) -> bool:
        """
        Check if caching is enabled for a category.

        Args:
            category (CacheCategory): The cache category to check.

        Returns:
            bool: True if caching is enabled for the category, False otherwise.

        """
        # Check if category is supported
        if category not in self.list_cache_categories():
            return False

        config = self._config.get_category_config(category)
        return config.enabled

    def get_category_config(self, category: CacheCategory) -> CategoryConfig:
        """
        Get configuration for a specific cache category.

        Args:
            category (CacheCategory): The cache category to get the configuration for.

        Returns:
            CategoryConfig: The configuration object for the specified category.

        """
        return self._config.get_category_config(category)
