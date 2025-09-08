from enum import StrEnum
from typing import Any, Callable, Mapping, Optional

from httpx import URL, AsyncBaseTransport, AsyncClient, Headers, Request, Response
from httpx._client import EventHook
from httpx._config import (
    DEFAULT_LIMITS,
    DEFAULT_MAX_REDIRECTS,
    DEFAULT_TIMEOUT_CONFIG,
    Limits,
)
from httpx._types import (
    AuthTypes,
    CertTypes,
    CookieTypes,
    HeaderTypes,
    QueryParamTypes,
    TimeoutTypes,
)

from core_infinity_stones.core.utils.helpers import create_short_unique_id, mask_str
from core_infinity_stones.logging import (
    IncomingResponseEvent,
    Logger,
    OutgoingRequestEvent,
)


class LoggingVerbosity(StrEnum):
    LOW = "LOW"
    """Only log request and response metadata (method, URL, status code, duration)."""

    MEDIUM = "MEDIUM"
    """Log request and response headers in addition to metadata."""

    HIGH = "HIGH"
    """Log request and response bodies truncated to a 1000 chars in addition to metadata and headers."""

    FULL = "FULL"
    """Log request and response full bodies in addition to metadata and headers."""

    @property
    def should_log_headers(self) -> bool:
        return self in {LoggingVerbosity.MEDIUM, LoggingVerbosity.HIGH}

    @property
    def should_log_body(self) -> bool:
        return self == LoggingVerbosity.HIGH

    @property
    def should_truncate_body(self) -> bool:
        return self != LoggingVerbosity.FULL


class HttpxClientWithLogging(AsyncClient):
    def __init__(
        self,
        logger: Logger,
        auth: AuthTypes | None = None,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        cert: CertTypes | None = None,
        http1: bool = True,
        http2: bool = False,
        timeout: TimeoutTypes = DEFAULT_TIMEOUT_CONFIG,
        follow_redirects: bool = False,
        limits: Limits = DEFAULT_LIMITS,
        max_redirects: int = DEFAULT_MAX_REDIRECTS,
        event_hooks: None | (Mapping[str, list[EventHook]]) = None,
        base_url: URL | str = "",
        transport: AsyncBaseTransport | None = None,
        trust_env: bool = True,
        default_encoding: str | Callable[[bytes], str] = "utf-8",
        request_verbosity_level: LoggingVerbosity = LoggingVerbosity.MEDIUM,
        response_verbosity_level: LoggingVerbosity = LoggingVerbosity.MEDIUM,
    ) -> None:
        event_hooks_with_logging: Optional[Mapping[str, list[Callable[..., Any]]]] = None

        request_event_hooks = event_hooks.get("request", []) if event_hooks else []
        response_event_hooks = event_hooks.get("response", []) if event_hooks else []

        request_id = create_short_unique_id()

        request_logger = self.create_request_logger(request_verbosity_level, logger, request_id)
        response_logger = self.create_response_logger(response_verbosity_level, logger, request_id)

        event_hooks_with_logging = {
            "request": [*request_event_hooks, request_logger],
            "response": [*response_event_hooks, response_logger],
        }

        super().__init__(
            auth=auth,
            params=params,
            headers=headers,
            cookies=cookies,
            cert=cert,
            http1=http1,
            http2=http2,
            timeout=timeout,
            follow_redirects=follow_redirects,
            limits=limits,
            max_redirects=max_redirects,
            event_hooks=event_hooks_with_logging or event_hooks,
            base_url=base_url,
            transport=transport,
            trust_env=trust_env,
            default_encoding=default_encoding,
        )

    def create_request_logger(
        self, verbosity_level: LoggingVerbosity, logger: Logger, request_id: str
    ) -> Callable[[Request], None]:
        should_log_headers = verbosity_level.should_log_headers
        should_log_body = verbosity_level.should_log_body
        should_truncate_body = verbosity_level.should_truncate_body

        def request_logger(request: Request) -> None:
            request_body = None

            if should_log_body:
                request_body = request.content[:1000] if should_truncate_body else request.content

            headers = obfuscate_headers(request.headers) if should_log_headers else None

            logger.info(
                OutgoingRequestEvent(
                    request_id=request_id,
                    method=request.method,
                    url=str(request.url),
                    headers=headers,
                    body=request_body,
                    verbosity_level=verbosity_level,
                )
            )

        return request_logger


    def create_response_logger(
        self, verbosity_level: LoggingVerbosity, logger: Logger, request_id: str
    ) -> Callable[[Response], None]:
        should_log_headers = verbosity_level.should_log_headers
        should_log_body = verbosity_level.should_log_body
        should_truncate_body = verbosity_level.should_truncate_body

        def response_logger(response: Response) -> None:
            request = response.request
            response_body = None

            if should_log_body:
                response_body = response.text[:1000] if should_truncate_body else response.text

            headers = obfuscate_headers(request.headers) if should_log_headers else None

            logger.info(
                IncomingResponseEvent(
                    request_id=request_id,
                    method=request.method,
                    url=str(request.url),
                    status_code=response.status_code,
                    duration_ms=response.elapsed.total_seconds() * 1000,
                    headers=headers,
                    body=response_body,
                    verbosity_level=verbosity_level,
                )
            )

        return response_logger


def obfuscate_headers(headers: Headers) -> dict[str, str]:
    """
    Return a copy of headers with sensitive values partially obfuscated.
    Sensitive fields are detected by common HTTP header naming conventions.
    """
    obfuscated = {}

    for key, value in headers.items():
        lower_key = key.lower()

        is_sensitive_header = any( # Check if the header key contains any of the sensitive keywords
            sensitive in lower_key
            for sensitive in [
                "authorization",
                "api-key",
                "apikey",
                "secret",
                "token",
                "password",
                "passwd",
            ]
        )

        if is_sensitive_header:
            obfuscated[key] = mask_str(value)

        else:
            obfuscated[key] = value

    return obfuscated