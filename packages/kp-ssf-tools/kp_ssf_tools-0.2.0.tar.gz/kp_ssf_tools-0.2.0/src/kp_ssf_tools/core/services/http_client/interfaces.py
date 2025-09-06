"""HTTP client service interface for dependency injection."""

from abc import abstractmethod
from collections.abc import Callable, Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Protocol, runtime_checkable

from kp_ssf_tools.core.services.http_client.models import HttpResponse


@runtime_checkable
class HttpClientProtocol(Protocol):
    """Protocol defining the HTTP client interface for dependency injection."""

    @abstractmethod
    def get(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, str] | None = None,
        **kwargs: object,
    ) -> HttpResponse:
        """
        Execute GET request.

        Args:
            url: Target URL
            headers: Optional request headers
            params: Optional query parameters
            **kwargs: Additional request options

        Returns:
            HTTP response wrapper

        Raises:
            NetworkError: When request fails

        """
        ...

    @abstractmethod
    def post(
        self,
        url: str,
        data: bytes | str | dict[str, object] | None = None,
        json: dict[str, object] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: object,
    ) -> HttpResponse:
        """
        Execute POST request.

        Args:
            url: Target URL
            data: Request body data
            json: JSON data to send
            headers: Optional request headers
            **kwargs: Additional request options

        Returns:
            HTTP response wrapper

        Raises:
            NetworkError: When request fails

        """
        ...

    @abstractmethod
    def download_file(
        self,
        url: str,
        file_path: Path,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> HttpResponse:
        """
        Download file with optional progress tracking.

        Args:
            url: File URL to download
            file_path: Destination file path
            progress_callback: Optional progress callback function

        Returns:
            HTTP response wrapper

        Raises:
            NetworkError: When download fails

        """
        ...

    @abstractmethod
    def head(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        **kwargs: object,
    ) -> HttpResponse:
        """
        Execute HEAD request.

        Args:
            url: Target URL
            headers: Optional request headers
            **kwargs: Additional request options

        Returns:
            HTTP response wrapper

        Raises:
            NetworkError: When request fails

        """
        ...

    @abstractmethod
    def is_url_accessible(self, url: str) -> bool:
        """
        Check if URL is accessible without downloading content.

        Args:
            url: URL to check

        Returns:
            True if URL is accessible, False otherwise

        """
        ...

    @abstractmethod
    @contextmanager
    def session(self) -> Generator[object]:
        """
        Context manager for persistent session.

        Yields:
            HTTP client session

        """
        ...

    @abstractmethod
    def clear_cache(self) -> None:
        """Clear the response cache."""
        ...
