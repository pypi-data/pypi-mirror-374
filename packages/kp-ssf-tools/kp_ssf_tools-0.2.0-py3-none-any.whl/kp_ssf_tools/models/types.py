"""Common Types used throughout the toolkit."""

from pathlib import Path

type PathLike = Path | str

__all__: list[str] = [
    "PathLike",
]
