"""Volatility sub-command implementation."""

from pathlib import Path
from typing import TYPE_CHECKING

import rich_click as click
from dependency_injector.wiring import Provide, inject
from pydantic import ValidationError

from kp_ssf_tools.containers.application import ApplicationContainer
from kp_ssf_tools.volatility.models import ImagePlatforms, VolatilityInputModel
from kp_ssf_tools.volatility.processor import run_volatility_workflow

if TYPE_CHECKING:
    from kp_ssf_tools.core.services.rich_output.service import RichOutputService


@click.command()
@click.argument("image_file", type=click.Path(exists=True, path_type=Path))
@click.argument(
    "image_platform",
    type=click.Choice(
        ["windows", "mac", "linux"],
        case_sensitive=False,
    ),
)
@click.argument(
    "interesting_processes_file",
    type=click.Path(
        exists=True,
        path_type=Path,
    ),
)
@click.option(
    "--pid-list-file",
    type=click.Path(path_type=Path),
    help="Path to PID List output file (default: pid-list.txt)",
)
@click.option(
    "--results-dir",
    type=click.Path(path_type=Path),
    help="Results directory path (default: volatility/{image_file.stem} relative to image file)",
)
@inject
def volatility(  # noqa: PLR0913  IGNORE for now until we refactor the volatility command
    image_file: Path,
    image_platform: str,
    interesting_processes_file: Path,
    pid_list_file: Path | None,
    results_dir: Path | None,
    rich_output: "RichOutputService" = Provide[ApplicationContainer.core.rich_output],
) -> None:
    """
    Run Volatility-based workflow for forensic memory analysis.

    This command performs a complete forensic memory analysis workflow using Volatility:

    1. Extracts process list from the memory image
    2. Identifies interesting processes based on provided list
    3. Extracts file handles for each interesting process
    4. Creates memory dumps for each interesting process

    **Arguments:**
    ```
    IMAGE_FILE              Path to the RAM image file
    IMAGE_PLATFORM          Image platform (windows, mac, or linux)
    interesting_processes_file    Path to file containing interesting process names (one per line)
    ```

    **Examples:**
    ```
    # Basic usage
    ssf_tools volatility memory.dd windows interesting-processes.txt

    # With custom results directory
    ssf_tools volatility memory.dd windows processes.txt --results-dir ./analysis

    # With custom PID list file name
    ssf_tools volatility memory.dd linux processes.txt --pid-list-file custom-pids.txt
    ```
    """
    try:
        # Create and validate input model
        input_model = VolatilityInputModel(
            image_file=image_file,
            image_platform=ImagePlatforms(image_platform.lower()),  # Cast to enum
            pid_list_file=pid_list_file,
            interesting_processes_file=interesting_processes_file,
            results_dir=results_dir,
        )

    except ValidationError as e:
        # Display validation errors using Rich
        rich_output.error(f"Invalid platform '{image_platform}'.")
        rich_output.print(
            f"Must be one of: {', '.join([p.value for p in ImagePlatforms])}",
        )

        # Show detailed validation errors
        for error in e.errors():
            field = error["loc"][0] if error["loc"] else "unknown"
            message = error["msg"]
            rich_output.print(f"  • {field}: {message}")

        valid_platforms = ", ".join([p.value for p in ImagePlatforms])
        error_msg = f"Platform must be one of: {valid_platforms}"
        raise click.BadParameter(error_msg) from e

    except (OSError, ValueError) as e:
        rich_output.error(f"Input validation failed: {e}")
        raise click.ClickException(str(e)) from e

    # Run the workflow
    try:
        run_volatility_workflow(input_model)

    except KeyboardInterrupt:
        rich_output.warning("Workflow interrupted by user")
        raise click.Abort from None

    except (OSError, ValueError, RuntimeError) as e:
        rich_output.error(f"Workflow failed: {e}")
        raise click.ClickException(str(e)) from e
