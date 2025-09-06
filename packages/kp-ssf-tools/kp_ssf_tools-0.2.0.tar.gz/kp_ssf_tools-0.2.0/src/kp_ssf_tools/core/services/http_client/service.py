"""HTTP client service implementation with dependency injection."""

import time
from collections.abc import Callable, Generator
from contextlib import contextmanager
from pathlib import Path
from types import TracebackType

import httpx

from kp_ssf_tools.core.services.http_client.models import (
    HttpConfig,
    HttpConnectionError,
    HttpError,
    HttpResponse,
    HttpTimeoutError,
    NetworkError,
    RequestMethod,
    RetryStrategy,
)
from kp_ssf_tools.core.services.rich_output.interfaces import RichOutputProtocol


class HttpClientService:
    """HTTP client service implementing HttpClientProtocol."""

    def __init__(
        self,
        config: HttpConfig | None = None,
        output: RichOutputProtocol | None = None,
    ) -> None:
        """
        Initialize HTTP client service.

        Args:
            config: HTTP client configuration
            output: Rich output service for logging and user feedback

        """
        self.config = config or HttpConfig()
        self.output = output
        self._client: httpx.Client | None = None
        self._cache: dict[str, tuple[HttpResponse, float]] = {}

    def _create_client(self) -> httpx.Client:
        """Create configured httpx client."""
        return httpx.Client(
            timeout=self.config.timeout_seconds,
            follow_redirects=self.config.follow_redirects,
            verify=self.config.verify_ssl,
            limits=httpx.Limits(max_connections=self.config.max_connections),
            headers={"User-Agent": self.config.user_agent},
        )

    @property
    def client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = self._create_client()
        return self._client

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
        return self._execute_with_retry(
            RequestMethod.GET,
            url,
            headers=headers,
            params=params,
            **kwargs,
        )

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
        return self._execute_with_retry(
            RequestMethod.POST,
            url,
            data=data,
            json=json,
            headers=headers,
            **kwargs,
        )

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
        return self._execute_with_retry(
            RequestMethod.HEAD,
            url,
            headers=headers,
            **kwargs,
        )

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

        def download_attempt() -> HttpResponse:
            """Single download attempt."""
            start_time = time.time()

            try:
                with self.client.stream("GET", url) as response:
                    response.raise_for_status()

                    # Get content length for progress tracking
                    content_length = int(response.headers.get("content-length", 0))

                    # Ensure parent directory exists
                    file_path.parent.mkdir(parents=True, exist_ok=True)

                    downloaded = 0
                    with file_path.open("wb") as file:
                        for chunk in response.iter_bytes(chunk_size=8192):
                            file.write(chunk)
                            downloaded += len(chunk)

                            if progress_callback and content_length > 0:
                                progress_callback(downloaded, content_length)

                    elapsed = time.time() - start_time

                    return HttpResponse(
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        content=b"",  # Don't store large file content
                        text="",
                        url=str(response.url),
                        elapsed_seconds=elapsed,
                    )

            except httpx.TimeoutException as exc:
                msg = f"Download timeout for {url}"
                raise HttpTimeoutError(msg, url=url) from exc
            except httpx.ConnectError as exc:
                msg = f"Connection failed for {url}"
                raise HttpConnectionError(
                    msg,
                    url=url,
                ) from exc
            except httpx.HTTPStatusError as exc:
                msg = f"HTTP error {exc.response.status_code} for {url}"
                raise HttpError(
                    msg,
                    url=url,
                    status_code=exc.response.status_code,
                ) from exc
            except Exception as exc:
                msg = f"Download failed for {url}"
                raise NetworkError(msg, url=url) from exc

        return self._retry_operation(download_attempt, url)

    def is_url_accessible(self, url: str) -> bool:
        """
        Check if URL is accessible without downloading content.

        Args:
            url: URL to check

        Returns:
            True if URL is accessible, False otherwise

        """
        try:
            response = self.head(url)
        except NetworkError:
            return False
        else:
            return response.is_success

    @contextmanager
    def session(self) -> Generator[httpx.Client]:
        """
        Context manager for persistent session.

        Yields:
            HTTP client session

        """
        client = self._create_client()
        try:
            yield client
        finally:
            client.close()

    def clear_cache(self) -> None:
        """Clear the response cache."""
        self._cache.clear()

    def _execute_with_retry(
        self,
        method: RequestMethod,
        url: str,
        **kwargs: object,
    ) -> HttpResponse:
        """Execute HTTP request with retry logic."""

        def request_attempt() -> HttpResponse:
            """Single request attempt."""
            start_time = time.time()

            try:
                response = self.client.request(method.value, url, **kwargs)  # type: ignore[arg-type]
                elapsed = time.time() - start_time

                return HttpResponse(
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    content=response.content,
                    text=response.text,
                    url=str(response.url),
                    elapsed_seconds=elapsed,
                )

            except httpx.TimeoutException as exc:
                msg = f"Request timeout for {url}"
                raise HttpTimeoutError(msg, url=url) from exc
            except httpx.ConnectError as exc:
                msg = f"Connection failed for {url}"
                raise HttpConnectionError(msg, url=url) from exc
            except httpx.HTTPStatusError as exc:
                msg = f"HTTP error {exc.response.status_code} for {url}"
                raise HttpError(
                    msg,
                    url=url,
                    status_code=exc.response.status_code,
                ) from exc
            except Exception as exc:
                msg = f"Request failed for {url}"
                raise NetworkError(msg, url=url) from exc

        return self._retry_operation(request_attempt, url)

    def _retry_operation(
        self,
        operation: Callable[[], HttpResponse],
        url: str,
    ) -> HttpResponse:
        """Execute operation with configured retry strategy."""
        last_exception: NetworkError | None = None

        for attempt in range(self.config.max_retries + 1):
            try:
                response = operation()

                # Mark successful retry if we had previous failures
                if last_exception and attempt > 0 and self.output:
                    self.output.success(
                        f"Request succeeded after {attempt} retry attempts for {url}",
                    )

            except NetworkError as exc:
                last_exception = exc
                exc.retry_attempted = attempt > 0

                # Don't retry on final attempt
                if attempt == self.config.max_retries:
                    break

                # Calculate delay for next attempt
                delay = self._calculate_retry_delay(attempt + 1)

                # Log retry attempt with delay information
                if self.output:
                    self.output.warning(
                        f"Request failed for {url}, retrying in {delay:.1f}s "
                        f"(attempt {attempt + 1}/{self.config.max_retries})",
                    )

                time.sleep(delay)
            else:
                return response

        # All retries exhausted
        if last_exception:
            raise last_exception

        # Should not reach here, but just in case
        msg = f"Request failed for {url}"
        raise NetworkError(msg, url=url)

    def _calculate_retry_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt based on strategy."""
        if self.config.retry_strategy == RetryStrategy.NONE:
            return 0.0

        base_delay = self.config.base_delay_seconds

        if self.config.retry_strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = base_delay * (2 ** (attempt - 1))
        elif self.config.retry_strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = base_delay * attempt
        else:  # FIXED_DELAY
            delay = base_delay

        return float(min(delay, self.config.max_delay_seconds))

    def __enter__(self) -> "HttpClientService":
        """Context manager entry."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Context manager exit with cleanup."""
        if self._client:
            self._client.close()
            self._client = None
