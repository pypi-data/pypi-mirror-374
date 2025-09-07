import asyncio
import copy
import logging
from types import TracebackType
from typing import Any, Optional, Union

import httpx
from httpx._config import DEFAULT_TIMEOUT_CONFIG

from .. import get_meta
from ..config import ClientOptions, RateLimitConfig
from ..constants import GEOCODE_BASE_URL, PLACES_BASE_URL, SENSITIVE_DATA
from ..settings import get_config
from ._auth import (
    AuthMode,
    BaseAuth,
    GoogleADCAuth,
    HeaderApiKeyAuth,
    NoAuth,
    QueryApiKeyAuth,
)
from ._rate_limiter import AsyncRateLimiter
from ._retry import RetryConfig, default_retry_classifier, with_retries

PACKAGE_NAME, PACKAGE_VERSION = get_meta()
DEFAULT_USER_AGENT = f"{PACKAGE_NAME}/{PACKAGE_VERSION}"


class BaseGoogleMapsClient:
    """
    Shared scaffolding for Google Places / Geocoding async clients.

    Contract
    --------
    - If `self.base_url` is set, pass relative paths to `_request()`.
    - If `self.base_url` is empty/None, pass absolute URLs to `_request()`.

    Example (later):
        await self._request("GET", "/nearbysearch/json", params={...})
    """

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        auth_mode: Optional[AuthMode] = None,
        options: Optional[ClientOptions] = None,
        _query_api_key: bool = False,
    ) -> None:
        self.options = options or ClientOptions()
        self._logger = self._init_logger(self.options)
        self._client: Optional[httpx.AsyncClient] = None
        self._owns_client = self.options.http_client is None
        self.options.adc_scopes = (
            self.options.adc_scopes or get_config().google_adc_scopes
        )

        # Resolve auth priority
        if api_key is None:
            secret_str = get_config().google_places_api_key
            resolved_api_key = secret_str.get_secret_value() if secret_str else None
        else:
            resolved_api_key = api_key

        if auth_mode is not None:
            if auth_mode == AuthMode.API_KEY:
                if not resolved_api_key:
                    raise ValueError(
                        "AuthMode.API_KEY chosen but no API key provided or in environment."
                    )

                self._auth: BaseAuth = (
                    QueryApiKeyAuth(resolved_api_key)
                    if _query_api_key
                    else HeaderApiKeyAuth(resolved_api_key)
                )
            elif auth_mode == AuthMode.ADC:
                self._auth = GoogleADCAuth(
                    skew_seconds=self.options.retry.adc_clock_skew,
                    scopes=self.options.adc_scopes,
                )
            elif auth_mode == AuthMode.NONE:
                self._auth = NoAuth()
            else:  # pragma: no cover - defensive
                self._auth = NoAuth()  # type: ignore[unreachable]
        else:
            if resolved_api_key:
                self._auth = (
                    QueryApiKeyAuth(resolved_api_key)
                    if _query_api_key
                    else HeaderApiKeyAuth(resolved_api_key)
                )
            else:
                self._auth = GoogleADCAuth(
                    skew_seconds=self.options.retry.adc_clock_skew,
                    scopes=self.options.adc_scopes,
                )

        self._auth_mode = getattr(self._auth, "mode", AuthMode.NONE)

        # Rate limiter
        self._rate_limiter = AsyncRateLimiter(self.options.rate_limit.qpm)

        # Retry classifier (optionally overridden)
        self._retry_classifier = (
            self.options.retry_classifier
            or default_retry_classifier(self.options.retry)
        )

        # Base URL used for relative paths
        self.base_url = self.options.base_url

        self._logger.debug(
            "Initialized BaseGoogleMapsClient(auth_mode=%s, qpm=%s, base_url=%s)",
            self._auth_mode.value,
            self.options.rate_limit.qpm,
            self.base_url,
        )

    # ----- logging -----

    def _init_logger(self, options: ClientOptions) -> logging.Logger:
        logger = options.logger or logging.getLogger("gmaps")
        if options.logger is None:
            if options.enable_logging and not logger.handlers:
                handler = logging.StreamHandler()
                fmt = logging.Formatter(
                    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
                )
                handler.setFormatter(fmt)
                logger.addHandler(handler)
                logger.setLevel(logging.INFO)
                logger.propagate = False  # avoid duplicate logs to root
        # If a custom logger is supplied, caller configures it (documented behavior).
        return logger

    # ----- lifecycle -----

    async def __aenter__(self) -> "BaseGoogleMapsClient":
        self._ensure_client()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        await self.aclose()

    def __del__(self) -> None:  # best-effort cleanup; cannot await here
        # Safely probe without raising; don't manipulate the loop here.
        client = getattr(self, "_client", None)
        if isinstance(client, httpx.AsyncClient) and not getattr(
            client, "is_closed", True
        ):
            self._logger.debug("AsyncClient still open at GC; transport will be GC'd")

    def _ensure_client(self) -> None:
        if self._client is not None:
            return
        # Ensure a non-empty User-Agent
        ua = self.options.user_agent or DEFAULT_USER_AGENT
        headers = {"User-Agent": ua, **(self.options.headers or {})}
        timeout = self._coerce_timeout(self.options.timeout)
        if self._owns_client:
            self._client = httpx.AsyncClient(
                base_url=self.base_url or "",
                headers=headers,
                timeout=timeout,
                http2=self.options.http2,
                transport=self.options.transport,
                verify=self.options.verify,
                proxy=self.options.proxy,
            )
        else:
            self._client = self.options.http_client

    @property
    def client(self) -> httpx.AsyncClient:
        self._ensure_client()
        if self._client is None:
            raise RuntimeError("HTTP client not initialized.")
        return self._client

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None
            self._logger.debug("httpx.AsyncClient closed")

    def close(self) -> None:
        """
        Synchronous best-effort close for cases where you cannot `await aclose()`.
        Will only run if there is no running event loop in this thread.
        """
        if self._client is None:
            return
        try:
            asyncio.get_running_loop()
            # If an event loop is running, prefer `await aclose()`.
            self._logger.warning(
                "close() called with a running loop; skipping. Use `await aclose()` instead."
            )
        except RuntimeError:
            asyncio.run(self.aclose())

    # ---------- Utilities ----------

    @staticmethod
    def _coerce_timeout(val: Optional[Union[float, httpx.Timeout]]) -> httpx.Timeout:
        if isinstance(val, (int, float)):
            return httpx.Timeout(float(val))
        if isinstance(val, httpx.Timeout):
            return val
        return DEFAULT_TIMEOUT_CONFIG

    # ----- configuration hooks -----

    def set_rate_limit(self, qpm: Optional[int]) -> None:
        if qpm is not None and not (1 <= qpm <= 1000):
            raise ValueError("qpm must be between 1 and 1000")
        self._rate_limiter = AsyncRateLimiter(qpm)
        self.options.rate_limit.qpm = qpm
        self._logger.info("Rate limit updated: qpm=%s", qpm)

    def set_retry_config(self, retry: RetryConfig) -> None:
        self.options.retry = retry
        self._retry_classifier = default_retry_classifier(retry)
        self._logger.info("Retry config updated: %s", retry)

    @staticmethod
    def redact_url(url: httpx.URL) -> str:
        """Redact sensitive data from the URL."""
        for sensitive in SENSITIVE_DATA:
            if sensitive in url.params.keys():
                url = url.copy_remove_param(sensitive)

        return str(url)

    # ----- request pipeline (no actual endpoint wiring) -----

    async def _request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[httpx.QueryParams] = None,
        headers: Optional[dict[str, str]] = None,
        json: Optional[dict[str, Any]] = None,
        data: Optional[dict[str, Any]] = None,
        files: Optional[dict[str, Any]] = None,
        timeout: Optional[Union[float, httpx.Timeout]] = None,
    ) -> httpx.Response:
        """
        Protected request pipeline to be used by service modules.

        Steps:
          - Ensure client
          - Rate-limit acquire
          - Auth injection (API key or ADC bearer)
          - Send via httpx with retries & Retry-After support
        """
        self._ensure_client()
        if self._client is None:  # pragma: no cover
            raise RuntimeError("HTTP client not initialized.")

        # Enforce base_url contract if a relative URL is provided
        if not (url.startswith("http://") or url.startswith("https://")):
            if not (self.base_url and self.base_url.strip()):
                raise ValueError(
                    "Relative URL provided but base_url is not set. "
                    "Either set a base_url on the client or pass an absolute URL."
                )

        await self._rate_limiter.acquire()

        # Build request parts
        req_headers: dict[str, str] = {}
        if headers:
            req_headers.update(headers)

        req_params = httpx.QueryParams(params)

        # Inject auth
        req_params = await self._auth.inject(req_headers, req_params)

        # Dispatcher wrapped in retries
        async def _do_send() -> httpx.Response:
            resp = await self.client.request(
                method=method,
                url=url,
                params=req_params,
                headers=req_headers,
                json=json,
                data=data,
                files=files,
                timeout=(
                    self._coerce_timeout(timeout)
                    if timeout is not None
                    else self._coerce_timeout(self.options.timeout)
                ),
            )
            try:
                resp.raise_for_status()
            except httpx.HTTPStatusError as e:
                response_json = None
                response_text = None
                try:
                    response_json = e.response.json()
                except Exception:
                    response_text = e.response.text

                redacted_url = self.redact_url(e.request.url)
                self._logger.error(
                    "HTTP request failed",
                    extra={
                        "status_code": e.response.status_code,
                        "url": redacted_url,
                        "method": e.request.method,
                        "response": response_json or response_text,
                    },
                )
                raise
            return resp

        if not self.options.retry.enabled:
            return await _do_send()

        def _classifier(
            _resp: Optional[httpx.Response], _exc: Optional[BaseException]
        ) -> bool:
            if _resp is None and isinstance(_exc, httpx.HTTPStatusError):
                _resp = _exc.response
            return self._retry_classifier(_resp, _exc)

        return await with_retries(
            _do_send,
            retry_conf=self.options.retry,
            classify=_classifier,
            delay_override=self.options.retry_delay_override,
        )

    # ----- diagnostics -----

    @property
    def auth_mode(self) -> AuthMode:
        return self._auth_mode

    def info(self) -> dict[str, Any]:
        """
        Lightweight diagnostics for debugging. Timeouts are normalized.
        """
        t = self._coerce_timeout(self.options.timeout)
        timeouts = {
            "connect": t.connect,
            "read": t.read,
            "write": t.write,
            "pool": t.pool,
        }
        return {
            "auth_mode": self.auth_mode.value,
            "qpm": self.options.rate_limit.qpm,
            "retry_enabled": self.options.retry.enabled,
            "retry_on_status": list(self.options.retry.retry_on_status),
            "base_url": self.base_url,
            "http2": self.options.http2,
            "timeouts": timeouts,
        }


class PlacesBaseClient(BaseGoogleMapsClient):
    """Specialization for Places API (sets default base_url and service-default QPM)."""

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        auth_mode: Optional[AuthMode] = None,
        options: Optional[ClientOptions] = None,
        qpm: Optional[int] = None,
    ) -> None:
        opts = copy.copy(options) if options else None
        opts = opts or ClientOptions()
        if opts.base_url is None:
            opts.base_url = PLACES_BASE_URL
        if opts.rate_limit.qpm is None:
            opts.rate_limit = RateLimitConfig.for_service("places", override_qpm=qpm)
        elif qpm is not None:
            opts.rate_limit.qpm = qpm
        super().__init__(
            api_key=api_key, auth_mode=auth_mode, options=opts, _query_api_key=False
        )


class GeocodingBaseClient(BaseGoogleMapsClient):
    """Specialization for Geocoding API (sets default base_url and service-default QPM)."""

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        auth_mode: Optional[AuthMode] = None,
        options: Optional[ClientOptions] = None,
        qpm: Optional[int] = None,
    ) -> None:
        opts = copy.copy(options) if options else None
        opts = opts or ClientOptions()
        if opts.base_url is None:
            opts.base_url = GEOCODE_BASE_URL
        if opts.rate_limit.qpm is None:
            opts.rate_limit = RateLimitConfig.for_service("geocoding", override_qpm=qpm)
        elif qpm is not None:
            opts.rate_limit.qpm = qpm
        super().__init__(
            api_key=api_key, auth_mode=auth_mode, options=opts, _query_api_key=True
        )
