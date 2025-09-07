import logging
from dataclasses import dataclass, field
from ssl import SSLContext
from typing import Callable, Optional, Union

import httpx
from httpx import _types as httpx_types

from . import get_meta
from .clients._retry import RetryConfig, default_retry_delay_override

PACKAGE_NAME, PACKAGE_VERSION = get_meta()
DEFAULT_USER_AGENT = f"{PACKAGE_NAME}/{PACKAGE_VERSION}"


@dataclass
class RateLimitConfig:
    """
    Per-instance QPM rate limit. Provide `qpm=None` to disable (not recommended).
    """

    qpm: Optional[int] = None

    @staticmethod
    def for_service(
        service: str, override_qpm: Optional[int] = None
    ) -> "RateLimitConfig":
        if override_qpm is not None:
            return RateLimitConfig(qpm=override_qpm)
        defaults = {
            "places": 60,  # conservative placeholders
            "geocoding": 60,
        }
        return RateLimitConfig(qpm=defaults.get(service, 60))


@dataclass
class ClientOptions:
    """
    Options to configure the base client.

    Advanced hooks:
    - retry_classifier: override retry decision logic without subclassing.
    - retry_delay_override: e.g., respect Retry-After; default provided.
    """

    # Rate limiting
    rate_limit: RateLimitConfig = field(default_factory=lambda: RateLimitConfig(qpm=60))

    # Retries
    retry: RetryConfig = field(default_factory=RetryConfig)
    retry_classifier: Optional[
        Callable[[Optional[httpx.Response], Optional[BaseException]], bool]
    ] = None
    retry_delay_override: Optional[
        Callable[[Optional[httpx.Response], Optional[BaseException]], Optional[float]]
    ] = default_retry_delay_override

    # HTTP
    timeout: Optional[Union[float, httpx.Timeout]] = None
    http2: bool = True
    headers: dict[str, str] = field(default_factory=dict)
    base_url: Optional[str] = None
    transport: Optional[httpx.AsyncBaseTransport] = None
    http_client: Optional[httpx.AsyncClient] = None
    verify: Union[SSLContext, str, bool] = True
    proxy: Optional[httpx_types.ProxyTypes] = None
    adc_scopes: Optional[tuple[str, ...]] = None
    # Misc
    user_agent: str = DEFAULT_USER_AGENT
    enable_logging: bool = True
    logger: Optional[logging.Logger] = None
