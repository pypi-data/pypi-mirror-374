"""HTTP client data models."""

from dataclasses import dataclass
from enum import StrEnum

# HTTP status code constants
HTTP_STATUS_OK = 200
HTTP_STATUS_REDIRECT_START = 300
HTTP_STATUS_CLIENT_ERROR_START = 400
HTTP_STATUS_SERVER_ERROR_START = 500
HTTP_STATUS_SERVER_ERROR_END = 600


class RequestMethod(StrEnum):
    """HTTP request methods."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    HEAD = "HEAD"
    PATCH = "PATCH"


class RetryStrategy(StrEnum):
    """Retry strategy types."""

    NONE = "none"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"


@dataclass
class HttpConfig:
    """HTTP client configuration."""

    timeout_seconds: float = 10.0
    max_retries: int = 3
    retry_strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    base_delay_seconds: float = 1.0
    max_delay_seconds: float = 60.0
    user_agent: str = "SSF-Tools/1.0"
    follow_redirects: bool = True
    verify_ssl: bool = True
    max_connections: int = 10
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600


@dataclass
class HttpResponse:
    """HTTP response wrapper."""

    status_code: int
    headers: dict[str, str]
    content: bytes
    text: str
    url: str
    elapsed_seconds: float
    from_cache: bool = False

    @property
    def is_success(self) -> bool:
        """Check if response indicates success."""
        return HTTP_STATUS_OK <= self.status_code < HTTP_STATUS_REDIRECT_START

    @property
    def is_client_error(self) -> bool:
        """Check if response indicates client error."""
        return (
            HTTP_STATUS_CLIENT_ERROR_START
            <= self.status_code
            < HTTP_STATUS_SERVER_ERROR_START
        )

    @property
    def is_server_error(self) -> bool:
        """Check if response indicates server error."""
        return (
            HTTP_STATUS_SERVER_ERROR_START
            <= self.status_code
            < HTTP_STATUS_SERVER_ERROR_END
        )


class NetworkError(Exception):
    """Base exception for network-related errors."""

    def __init__(
        self,
        message: str,
        *,
        url: str | None = None,
        status_code: int | None = None,
        retry_attempted: bool = False,
    ) -> None:
        super().__init__(message)
        self.url = url
        self.status_code = status_code
        self.retry_attempted = retry_attempted


class HttpTimeoutError(NetworkError):
    """Request timeout error."""


class HttpConnectionError(NetworkError):
    """Connection-related error."""


class HttpError(NetworkError):
    """HTTP protocol error."""
