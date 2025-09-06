"""
Unified Google Maps API client for both Places and Geocoding APIs.

This module provides the main GmapsClient class that offers a unified interface to both
the Google Places API (New) and Geocoding API through a single client instance.
"""

from __future__ import annotations

import logging
from types import TracebackType
from typing import Any, Optional

from ..config import ClientOptions
from ._auth import AuthMode
from ._clients import GeocodingClient, PlacesClient


class GmapsClient:
    """
    Unified async client for Google Maps APIs (Places + Geocoding).

    Basic Usage:
        ```python
        from gmaps import GmapsClient

        # Simple usage with API key
        async with GmapsClient(api_key="your-api-key") as client:
            # Use Places API
            places_response = await client.places.nearby_search_simple(
                latitude=37.7749, longitude=-122.4194, radius=1000
            )

            # Use Geocoding API
            geocode_response = await client.geocoding.geocode_simple(
                address="1600 Amphitheatre Parkway, Mountain View, CA"
            )
        ```

    Advanced Usage:
        ```python
        from gmaps import GmapsClient, ClientOptions, AuthMode
        import httpx

        # Full customization
        options = ClientOptions(
            timeout=httpx.Timeout(30.0),
            http2=False,
            enable_logging=True
        )

        async with GmapsClient(
            auth_mode=AuthMode.ADC,
            options=options,
            places_qpm=100,
            geocoding_qpm=50
        ) as client:
            # Access individual clients with shared config
            places_client = client.places
            geocoding_client = client.geocoding

            # Use any method from either client
            response = await places_client.text_search_simple(
                query="pizza restaurants near Times Square"
            )
        ```

    Authentication:
    - API Key: Pass api_key parameter or set GOOGLE_PLACES_API_KEY environment variable
    - ADC: Use auth_mode=AuthMode.ADC for Application Default Credentials
    - Auto-detection: Client automatically selects based on available credentials
    """

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        auth_mode: Optional[AuthMode] = None,
        options: Optional[ClientOptions] = None,
        places_qpm: Optional[int] = None,
        geocoding_qpm: Optional[int] = None,
    ) -> None:
        """
        Initialize unified Google Maps client.

        Args:
            api_key: Google Maps API key. If not provided, will use GOOGLE_PLACES_API_KEY env var
            auth_mode: Authentication mode (API_KEY or ADC). Auto-detected if not specified
            options: Client configuration options (shared by both APIs)
            places_qpm: Places API queries per minute rate limit. Uses service default if not specified
            geocoding_qpm: Geocoding API queries per minute rate limit. Uses service default if not specified

        Raises:
            ValueError: If auth_mode is API_KEY but no API key is provided
            RuntimeError: If ADC authentication is requested but google-auth is not installed

        Example:
            ```python
            # Simple initialization
            client = GmapsClient(api_key="your-api-key")

            # Advanced initialization
            client = GmapsClient(
                auth_mode=AuthMode.ADC,
                options=ClientOptions(timeout=30.0, http2=False),
                places_qpm=100,
                geocoding_qpm=50
            )
            ```
        """
        if api_key is not None and len(api_key) > 1000:
            raise ValueError("api_key must be <= 1000 characters")
        if places_qpm is not None and not (1 <= places_qpm <= 1000):
            raise ValueError("places_qpm must be between 1 and 1000")
        if geocoding_qpm is not None and not (1 <= geocoding_qpm <= 1000):
            raise ValueError("geocoding_qpm must be between 1 and 1000")
        # Store configuration for sub-clients
        self._api_key = api_key
        self._auth_mode = auth_mode
        self._options = options
        self._places_qpm = places_qpm
        self._geocoding_qpm = geocoding_qpm
        self._logger = self._init_logger(options)

        # Initialize sub-clients with shared configuration
        # Each client handles its own base URL and service-specific defaults
        self.places = PlacesClient(
            api_key=api_key,
            auth_mode=auth_mode,
            options=options,
            qpm=places_qpm,
        )

        self.geocoding = GeocodingClient(
            api_key=api_key,
            auth_mode=auth_mode,
            options=options,
            qpm=geocoding_qpm,
        )

    def _init_logger(self, options: Optional[ClientOptions]) -> logging.Logger:
        logger = (options and options.logger) or logging.getLogger("gmaps")
        if options and options.logger is None:
            if options.enable_logging and not logger.handlers:
                handler = logging.StreamHandler()
                fmt = logging.Formatter(
                    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
                )
                handler.setFormatter(fmt)
                logger.addHandler(handler)
                logger.setLevel(logging.INFO)
                logger.propagate = False
        return logger

    async def __aenter__(self) -> GmapsClient:
        """
        Async context manager entry.

        Initializes both Places and Geocoding clients and returns the unified client.
        """
        # Track which resources were successfully entered
        self._entered_clients = []

        try:
            await self.places.__aenter__()
            self._entered_clients.append("places")

            await self.geocoding.__aenter__()
            self._entered_clients.append("geocoding")

            return self
        except Exception:
            # Clean up any resources that were successfully entered
            await self._cleanup_entered_clients(None, None, None)
            raise

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """
        Async context manager exit.

        Properly closes both Places and Geocoding clients.
        """
        await self._cleanup_entered_clients(exc_type, exc_val, exc_tb)

    async def _cleanup_entered_clients(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Helper method to clean up only successfully entered clients."""
        cleanup_exceptions = []

        # Clean up in reverse order to handle dependencies properly
        for client_name in reversed(getattr(self, "_entered_clients", [])):
            client = getattr(self, client_name)
            try:
                await client.__aexit__(exc_type, exc_val, exc_tb)
            except Exception as cleanup_exc:
                self._logger.error(
                    f"Error cleaning up {client_name} client", exc_info=True
                )
                cleanup_exceptions.append(cleanup_exc)

        # Clear the tracking list
        self._entered_clients = []

        # Re-raise the first cleanup exception encountered
        if cleanup_exceptions:
            raise cleanup_exceptions[0]

    async def aclose(self) -> None:
        """
        Explicitly close both API clients.

        Call this if not using the async context manager pattern.
        """
        await self.places.aclose()
        await self.geocoding.aclose()

    def close(self) -> None:
        """
        Synchronous close for both API clients.

        This is a best-effort close that only works when no event loop is running.
        Prefer using the async context manager or await aclose().
        """
        self.places.close()
        self.geocoding.close()

    @property
    def auth_mode(self) -> AuthMode:
        """Get the authentication mode used by both clients."""
        return self.places.auth_mode

    def info(self) -> dict[str, Any]:
        """
        Get diagnostic information about both clients.

        Returns:
            Dict containing configuration info for both Places and Geocoding clients
        """
        return {
            "unified_client": True,
            "auth_mode": self.auth_mode.value,
            "places": self.places.info(),
            "geocoding": self.geocoding.info(),
        }

    def set_rate_limit(
        self, *, places_qpm: Optional[int] = None, geocoding_qpm: Optional[int] = None
    ) -> None:
        """
        Update rate limits for both API clients.

        Args:
            places_qpm: New Places API rate limit (QPM)
            geocoding_qpm: New Geocoding API rate limit (QPM)
        """
        if places_qpm is not None:
            self.places.set_rate_limit(places_qpm)
        if geocoding_qpm is not None:
            self.geocoding.set_rate_limit(geocoding_qpm)
