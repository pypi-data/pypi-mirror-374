# ruff: noqa: E402
"""
Google Maps API async client library.

This library provides async clients for Google Maps APIs with support for:
- Places API (New): nearby search, text search, place details, autocomplete
- Geocoding API: address to coordinates conversion and vice versa

Main exports:
- GmapsClient: Unified client for both APIs (recommended)
- PlacesClient: Dedicated Places API client
- GeocodingClient: Dedicated Geocoding API client
"""

from functools import lru_cache
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _version
from typing import Callable


def _get_meta_impl() -> tuple[str, str]:
    pkg_name = __name__.split(".")[0]
    try:
        return pkg_name, _version(pkg_name)
    except PackageNotFoundError:
        return pkg_name, "0.0.0+dev"


get_meta: Callable[[], tuple[str, str]] = lru_cache(maxsize=1)(_get_meta_impl)

from .clients import AuthMode, GeocodingClient, GmapsClient, PlacesClient, RetryConfig
from .config import ClientOptions, RateLimitConfig
from .models import (  # Component models; Location models; Request models; Enum models
    AutocompleteRequest,
    Circle,
    Component,
    ComponentFilter,
    DetailsRequest,
    EVConnectorType,
    ExtraComputations,
    GeocodingRequest,
    LatLng,
    LocationBias,
    LocationRestriction,
    NearbySearchRequest,
    PriceLevel,
    RankPreference,
    TextSearchRequest,
    Viewport,
    clear_custom_registries,
    get_custom,
    register_custom,
)

__all__ = [
    # Client classes
    "GmapsClient",
    "PlacesClient",
    "GeocodingClient",
    # Auth and config
    "AuthMode",
    "RetryConfig",
    "ClientOptions",
    "RateLimitConfig",
    # Request models
    "NearbySearchRequest",
    "TextSearchRequest",
    "DetailsRequest",
    "AutocompleteRequest",
    "GeocodingRequest",
    # Location models
    "LatLng",
    "Circle",
    "LocationRestriction",
    "LocationBias",
    "Viewport",
    # Component models
    "ComponentFilter",
    "Component",
    # Enum models
    "RankPreference",
    "PriceLevel",
    "EVConnectorType",
    "ExtraComputations",
    # Hook functions for custom registration
    "register_custom",
    "get_custom",
    "clear_custom_registries",
    # Utility
    "get_meta",
]
