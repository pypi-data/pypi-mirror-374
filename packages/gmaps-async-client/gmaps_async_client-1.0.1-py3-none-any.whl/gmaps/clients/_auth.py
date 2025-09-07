# _auth.py
import asyncio
import time
from collections.abc import MutableMapping
from enum import Enum
from typing import Optional

import httpx  # NEW: we now type against httpx.QueryParams


class AuthMode(Enum):
    API_KEY = "api_key"
    ADC = "adc"
    NONE = "none"  # explicit no-auth (testing)


class BaseAuth:
    """
    Strategy interface for auth. Implementations can inject headers/params.

    Contract:
      - `headers` is mutable; implementations MAY mutate it in place.
      - `params` is httpx.QueryParams (immutable); implementations MUST return
        a (possibly) updated instance.
    """

    mode: AuthMode = AuthMode.NONE

    async def inject(
        self, headers: MutableMapping[str, str], params: httpx.QueryParams
    ) -> httpx.QueryParams:  # pragma: no cover - interface
        raise NotImplementedError


class NoAuth(BaseAuth):
    mode = AuthMode.NONE

    async def inject(
        self, headers: MutableMapping[str, str], params: httpx.QueryParams
    ) -> httpx.QueryParams:
        return params


class HeaderApiKeyAuth(BaseAuth):
    mode = AuthMode.API_KEY

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    async def inject(
        self, headers: MutableMapping[str, str], params: httpx.QueryParams
    ) -> httpx.QueryParams:
        # Don't clobber if user explicitly set header.
        headers.setdefault("X-Goog-Api-Key", self.api_key)
        return params


class QueryApiKeyAuth(BaseAuth):
    mode = AuthMode.API_KEY

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    async def inject(
        self, headers: MutableMapping[str, str], params: httpx.QueryParams
    ) -> httpx.QueryParams:
        # If user already supplied ?key=..., don't override.
        if "key" in params:
            return params
        return params.set("key", self.api_key)


class GoogleADCAuth(BaseAuth):
    """
    Application Default Credentials (ADC) bearer token auth with token caching.

    We refresh only when (expiry - skew) <= now. google-auth is imported lazily.
    """

    mode = AuthMode.ADC

    def __init__(
        self, *, skew_seconds: float = 60.0, scopes: Optional[tuple[str, ...]] = None
    ) -> None:
        self._credentials = None  # set on first use
        self._token: Optional[str] = None
        self._expiry_ts: float = 0.0
        self._skew = skew_seconds
        self._lock = asyncio.Lock()
        self._SCOPES = scopes or ("https://www.googleapis.com/auth/cloud-platform",)
        try:
            import google.auth  # noqa: F401
        except (ImportError, ModuleNotFoundError) as exc:
            raise RuntimeError(
                "google-auth is required for ADC authentication. "
                "Install with `pip install google-auth` or use API key."
            ) from exc

    async def _maybe_refresh(self) -> None:
        now = time.time()
        if self._token and (self._expiry_ts - self._skew) > now:
            return
        async with self._lock:
            now2 = time.time()
            if self._token and (self._expiry_ts - self._skew) > now2:
                return

            def _sync_refresh() -> tuple[str, float]:
                import google.auth
                import google.auth.transport.requests

                credentials, _ = google.auth.default(scopes=list(self._SCOPES))
                request = google.auth.transport.requests.Request()
                credentials.refresh(request)
                token = credentials.token
                expiry_dt = getattr(credentials, "expiry", None)
                expiry_ts = (
                    expiry_dt.timestamp() if expiry_dt else (time.time() + 300.0)
                )
                return token, expiry_ts

            loop = asyncio.get_running_loop()
            token, expiry_ts = await loop.run_in_executor(None, _sync_refresh)
            self._token, self._expiry_ts = token, expiry_ts

    async def inject(
        self, headers: MutableMapping[str, str], params: httpx.QueryParams
    ) -> httpx.QueryParams:
        await self._maybe_refresh()
        if not self._token:  # pragma: no cover - defensive
            raise RuntimeError("ADC token acquisition failed.")
        # Don't clobber an explicit Authorization header
        headers.setdefault("Authorization", f"Bearer {self._token}")
        return params
