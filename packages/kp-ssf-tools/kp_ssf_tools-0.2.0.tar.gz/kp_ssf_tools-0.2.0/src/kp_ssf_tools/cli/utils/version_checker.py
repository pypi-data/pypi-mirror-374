"""Version checking utility for the KP Analysis Toolkit."""

import json
import sys
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen

from packaging import version

from kp_ssf_tools import __version__
from kp_ssf_tools.core.services.rich_output import RichOutputService


class VersionChecker:
    """Utility class to check for package updates on PyPI."""

    def __init__(
        self,
        rich_output: RichOutputService,
        package_name: str = "kp-ssf-tools",
    ) -> None:
        """
        Initialize the version checker.

        Args:
            rich_output: The RichOutputService instance for formatted output
            package_name: The PyPI package name to check for updates

        """
        self.package_name = package_name
        self.current_version = __version__
        self.rich_output = rich_output

    def check_for_updates(self, timeout: int = 5) -> tuple[bool, str | None]:
        """
        Check PyPI for available updates.

        Args:
            timeout: Timeout in seconds for the network request

        Returns:
            Tuple of (has_update, latest_version)
            - has_update: True if an update is available
            - latest_version: The latest version string, or None if check failed

        """
        try:
            url = f"https://pypi.org/pypi/{self.package_name}/json"
            # Only allow HTTPS URLs for security
            if not url.startswith("https://"):
                return False, None

            with urlopen(url, timeout=timeout) as response:  # noqa: S310
                data: dict[str, Any] = json.loads(response.read().decode())
                latest_version = data["info"]["version"]

            # Compare versions
            current = version.parse(self.current_version)
            latest = version.parse(latest_version)
        except (URLError, json.JSONDecodeError, KeyError, Exception):
            # Network error, JSON parsing error, or other issues
            return False, None
        else:
            return latest > current, latest_version

    def prompt_for_upgrade(self, latest_version: str, rich: RichOutputService) -> None:
        """
        Inform user about available upgrade and provide instructions.

        Args:
            latest_version: The latest available version
            rich: The RichOutputService instance for formatted output

        """
        # Use info() method for header since header() doesn't exist
        rich.info("📦 Update Available")

        # Get the command that was actually run
        actual_command = "ssf_tools"
        if len(sys.argv) > 0:
            # If running via python -m, show the expected command format
            if (
                sys.argv[0].endswith(("main.py", "__main__.py"))
                or "kp_ssf_tools" in sys.argv[0]
            ):
                actual_command = "ssf_tools"
            else:
                # Use the actual command if it looks like our CLI
                cmd_name = sys.argv[0]
                if "kp_ssf_tools" in cmd_name.lower() or cmd_name.endswith(".exe"):
                    actual_command = cmd_name

        # Create data dictionary for summary_panel with proper structure
        version_data: dict[str, object] = {
            "Current version": self.current_version,
            "Latest version": latest_version,
            "Upgrade command": f"pipx upgrade {self.package_name}",
            "Skip check option": f"{actual_command} --skip-update-check",
        }

        self.rich_output.summary_panel(
            "Upgrade Information",
            version_data,
        )

        self.rich_output.info(
            "The application will now exit. Please run the upgrade command above and then run your command again.",
        )
        self.rich_output.warning(
            "Note: Upgrade checks can be disabled using the --skip-update-check option.",
        )


def check_and_prompt_update(
    rich_output: RichOutputService,
    package_name: str = "kp-ssf-tools",
) -> None:
    """
    Check for updates and inform user if available.

    This function should be called at the start of CLI execution.
    If an update is available, it will display upgrade instructions and exit.

    Args:
        rich_output: The RichOutputService instance for formatted output
        package_name: The PyPI package name to check

    """
    checker = VersionChecker(rich_output, package_name)

    try:
        has_update, latest_version = checker.check_for_updates()

        if latest_version is None:
            # Network error or other issue - fail silently
            rich_output.debug("Unable to check for updates (network unavailable)")
            return

        if has_update and latest_version:
            checker.prompt_for_upgrade(latest_version, rich_output)
            sys.exit(0)  # Exit after showing upgrade instructions

    except Exception:  # noqa: BLE001, S110
        # Any unexpected error - fail silently and continue
        pass
