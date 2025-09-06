"""Main CLI entry point for SSF Tools."""

import rich_click as click

from kp_ssf_tools import __version__
from kp_ssf_tools.containers.application import ApplicationContainer

# Configure rich-click
click.rich_click.USE_RICH_MARKUP = True
click.rich_click.USE_MARKDOWN = True


@click.group(
    name="ssf_tools",
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.version_option(version=__version__, prog_name="SSF Tools")
@click.option(
    "--skip-update-check",
    is_flag=True,
    help="Skip checking for package updates",
)
def cli(*, skip_update_check: bool) -> None:
    """
    SSF Tools - Forensic Analysis Toolkit for cybersecurity professionals.

    A toolkit for software security assessments including memory analysis
    with Volatility, entropy analysis, credential discovery, and more.
    """
    # The skip_update_check parameter is handled in main() via argv parsing
    # This parameter exists only to show the option in --help


# Late import to avoid circular dependency
def register_commands() -> None:
    """Register all sub-commands."""
    from kp_ssf_tools.cli.commands.analyze import analyze_group
    from kp_ssf_tools.cli.commands.cache import cache_group
    from kp_ssf_tools.cli.commands.config import config_group
    from kp_ssf_tools.cli.commands.utils import utils_group
    from kp_ssf_tools.cli.commands.volatility import volatility

    cli.add_command(cache_group)
    cli.add_command(config_group)
    cli.add_command(analyze_group)
    cli.add_command(utils_group)
    cli.add_command(volatility)


def main() -> None:
    """Main entry point with DI container setup."""
    # Initialize the application container
    print("Initializing CLI...")
    container = ApplicationContainer()
    container.wire(
        modules=[
            "kp_ssf_tools.cli.commands.cache",
            "kp_ssf_tools.cli.commands.config",
            "kp_ssf_tools.cli.commands.analyze",
            "kp_ssf_tools.cli.commands.utils",
            "kp_ssf_tools.cli.commands.volatility",
        ],
    )

    # Register commands
    register_commands()

    try:
        # Check if --skip-update-check is present before running Click
        import sys

        skip_update_check = "--skip-update-check" in sys.argv

        # Perform version check unless skipped
        if not skip_update_check:
            try:
                from kp_ssf_tools.cli.utils.version_checker import (
                    check_and_prompt_update,
                )
                from kp_ssf_tools.core.services.rich_output.service import (
                    RichOutputService,
                )

                # Create a temporary RichOutputService for version checking
                rich_output = RichOutputService()
                check_and_prompt_update(rich_output)
            except Exception:  # noqa: BLE001, S110
                # If version checking fails, continue with normal execution
                # Silently ignore since this is a non-critical feature
                pass

        cli()
    finally:
        # Clean up container
        container.unwire()


if __name__ == "__main__":
    main()
