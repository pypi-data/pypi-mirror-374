"""CLI cache management commands."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import rich_click as click
from dependency_injector.wiring import Provide, inject

from kp_ssf_tools.containers.application import ApplicationContainer
from kp_ssf_tools.core.services.cache.models import CacheCategory

if TYPE_CHECKING:
    from datetime import timedelta

    from kp_ssf_tools.core.services.cache.interfacecs import CacheServiceProtocol
    from kp_ssf_tools.core.services.rich_output.interfaces import RichOutputProtocol


def _parse_time_delta(time_str: str) -> timedelta:
    """Parse time delta from string like '30d', '1w', '24h'."""
    from datetime import timedelta

    match = re.match(r"^(\d+)([dwh])$", time_str.lower())
    if not match:
        msg = "Invalid time format. Use format like '30d', '1w', '24h'"
        raise ValueError(msg)

    value = int(match.group(1))
    unit = match.group(2)

    if unit == "d":
        return timedelta(days=value)
    if unit == "w":
        return timedelta(weeks=value)
    if unit == "h":
        return timedelta(hours=value)

    msg = f"Unknown time unit: {unit}"
    raise ValueError(msg)


@click.group(name="cache")
def cache_group() -> None:
    """Cache management commands for SSF Tools."""


@click.command()
@inject
def show(
    cache_service: CacheServiceProtocol = Provide[ApplicationContainer.core.cache],
    output: RichOutputProtocol = Provide[ApplicationContainer.core.rich_output],
) -> None:
    """Show cache information and statistics."""
    try:
        cache_info = cache_service.get_cache_info()

        # Display cache overview
        output.info(f"Cache Directory: {cache_info.base_cache_dir}")
        output.info(f"Total Size: {cache_info.total_size_bytes / 1024 / 1024:.1f} MB")
        output.info(f"Total Items: {cache_info.total_items:,}")

        if cache_info.last_cleanup:
            output.info(f"Last Cleanup: {cache_info.last_cleanup}")
        else:
            output.info("Last Cleanup: Never")

        # Display category breakdown
        if cache_info.categories:
            table_data: list[dict[str, object]] = []
            for category_name, info in cache_info.categories.items():
                table_data.append(
                    {
                        "Category": category_name,
                        "Size": f"{info.size_bytes / 1024 / 1024:.1f} MB",
                        "Items": f"{info.item_count:,}",
                        "TTL": f"{info.ttl_hours}h",
                        "Oldest": info.oldest_item.strftime("%Y-%m-%d %H:%M")
                        if info.oldest_item
                        else "N/A",
                        "Newest": info.newest_item.strftime("%Y-%m-%d %H:%M")
                        if info.newest_item
                        else "N/A",
                    },
                )

            output.results_table(
                columns=["Category", "Size", "Items", "TTL", "Oldest", "Newest"],
                data=table_data,
                title="Cache Categories",
            )

    except OSError as e:
        output.error(f"Failed to get cache information: {e}")
        raise click.ClickException(str(e)) from e


@click.command()
@click.option(
    "--category",
    type=click.Choice([c.value for c in CacheCategory]),
    help="Clear specific cache category",
)
@click.option(
    "--older-than",
    help="Clear entries older than specified time (e.g., '30d', '1w', '24h')",
)
@click.option("--force", is_flag=True, help="Skip confirmation prompt")
@inject
def clear(
    category: str | None,
    older_than: str | None,
    *,
    force: bool,
    cache_service: CacheServiceProtocol = Provide[ApplicationContainer.core.cache],
    output: RichOutputProtocol = Provide[ApplicationContainer.core.rich_output],
) -> None:
    """Clear cache entries."""
    try:
        if not force:
            if category:
                message = f"Clear cache category '{category}'?"
            elif older_than:
                message = f"Clear cache entries older than {older_than}?"
            else:
                message = "Clear entire cache?"

            if not output.confirm_yes_no(message):
                output.info("Cache clear cancelled.")
                return

        if older_than:
            max_age = _parse_time_delta(older_than)
            cleared = cache_service.cleanup_expired(max_age)
        else:
            cache_category = CacheCategory(category) if category else None
            cleared = cache_service.clear_cache(cache_category)

        output.success(f"Cleared {cleared} cache entries.")

    except ValueError as e:
        output.error(f"Invalid time format: {e}")
        raise click.ClickException(str(e)) from e
    except OSError as e:
        output.error(f"Failed to clear cache: {e}")
        raise click.ClickException(str(e)) from e


@click.command()
@inject
def cleanup(
    cache_service: CacheServiceProtocol = Provide[ApplicationContainer.core.cache],
    output: RichOutputProtocol = Provide[ApplicationContainer.core.rich_output],
) -> None:
    """Remove expired cache entries."""
    try:
        removed = cache_service.cleanup_expired()
        output.success(f"Removed {removed} expired cache entries.")

    except OSError as e:
        output.error(f"Failed to cleanup cache: {e}")
        raise click.ClickException(str(e)) from e


@click.command()
@inject
def categories(
    cache_service: CacheServiceProtocol = Provide[ApplicationContainer.core.cache],
    output: RichOutputProtocol = Provide[ApplicationContainer.core.rich_output],
) -> None:
    """List available cache categories."""
    try:
        available_categories = cache_service.list_cache_categories()

        for category in available_categories:
            config = cache_service.get_category_config(category)
            enabled_status = "✓" if config.enabled else "✗"
            output.info(f"{enabled_status} {category.value} (TTL: {config.ttl_hours}h)")

    except OSError as e:
        output.error(f"Failed to list cache categories: {e}")
        raise click.ClickException(str(e)) from e


# Register commands
cache_group.add_command(show)
cache_group.add_command(clear)
cache_group.add_command(cleanup)
cache_group.add_command(categories)
