"""
Utility functions and helpers for tests.

This module provides reusable utilities for mocking and test setup
to avoid mypy method assignment issues and improve test readability.
"""

from typing import Any, Callable, Union
from unittest.mock import AsyncMock, Mock

from gmaps import GmapsClient


def mock_client_context_managers(client: GmapsClient) -> None:
    """
    Mock the context manager methods for a GmapsClient's sub-clients.

    Uses setattr to avoid mypy method assignment errors.

    Args:
        client: The GmapsClient instance to mock
    """
    # Mock places client context managers
    setattr(client.places, "__aenter__", AsyncMock(return_value=client.places))
    setattr(client.places, "__aexit__", AsyncMock(return_value=None))

    # Mock geocoding client context managers
    setattr(client.geocoding, "__aenter__", AsyncMock(return_value=client.geocoding))
    setattr(client.geocoding, "__aexit__", AsyncMock(return_value=None))


def mock_client_methods(client: GmapsClient, **method_mocks: Any) -> None:
    """
    Mock specific methods on a GmapsClient.

    Uses setattr to avoid mypy method assignment errors.

    Args:
        client: The GmapsClient instance to mock
        **method_mocks: Method names and their mock implementations

    Example:
        mock_client_methods(
            client,
            info=Mock(return_value={"unified_client": True}),
            set_rate_limit=Mock()
        )
    """
    for method_name, mock_impl in method_mocks.items():
        setattr(client, method_name, mock_impl)


def mock_sub_client_methods(
    client: GmapsClient,
    places_methods: Union[dict[str, Any], None] = None,
    geocoding_methods: Union[dict[str, Any], None] = None,
) -> None:
    """
    Mock methods on sub-clients (places and geocoding).

    Args:
        client: The GmapsClient instance
        places_methods: Dictionary of method names and mock implementations for places client
        geocoding_methods: Dictionary of method names and mock implementations for geocoding client

    Example:
        mock_sub_client_methods(
            client,
            places_methods={
                'nearby_search_simple': AsyncMock(return_value=mock_response),
                'info': Mock(return_value={"service": "places"})
            },
            geocoding_methods={
                'geocode_simple': AsyncMock(return_value=mock_response),
                'info': Mock(return_value={"service": "geocoding"})
            }
        )
    """
    if places_methods:
        for method_name, mock_impl in places_methods.items():
            setattr(client.places, method_name, mock_impl)

    if geocoding_methods:
        for method_name, mock_impl in geocoding_methods.items():
            setattr(client.geocoding, method_name, mock_impl)


def create_failing_context_manager(
    exception: Exception, on_enter: bool = True
) -> tuple[Callable[..., Any], Callable[..., Any]]:
    """
    Create context manager mocks that fail on enter or exit.

    Args:
        exception: The exception to raise
        on_enter: If True, fail on __aenter__, otherwise fail on __aexit__

    Returns:
        Tuple of (__aenter__ mock, __aexit__ mock)

    Example:
        aenter_mock, aexit_mock = create_failing_context_manager(
            RuntimeError("Init failed"),
            on_enter=True
        )
        setattr(client.places, '__aenter__', aenter_mock)
        setattr(client.places, '__aexit__', aexit_mock)
    """
    if on_enter:
        aenter_mock = AsyncMock(side_effect=exception)
        aexit_mock = AsyncMock(return_value=None)
    else:
        aenter_mock = AsyncMock(return_value=Mock())
        aexit_mock = AsyncMock(side_effect=exception)

    return aenter_mock, aexit_mock


def setup_context_manager_tracking(
    client: GmapsClient, tracker: dict[str, int]
) -> None:
    """
    Set up context manager methods that track call counts.

    Args:
        client: The GmapsClient instance
        tracker: Dictionary to store call counts
    """

    async def tracking_places_aenter():
        tracker.setdefault("enters", 0)
        tracker["enters"] += 1
        return client.places

    async def tracking_geocoding_aenter():
        tracker.setdefault("enters", 0)
        tracker["enters"] += 1
        return client.geocoding

    async def tracking_aexit(exc_type, exc, tb):
        tracker.setdefault("exits", 0)
        tracker["exits"] += 1
        return None

    setattr(client.places, "__aenter__", tracking_places_aenter)
    setattr(client.places, "__aexit__", tracking_aexit)
    setattr(client.geocoding, "__aenter__", tracking_geocoding_aenter)
    setattr(client.geocoding, "__aexit__", tracking_aexit)


class MockResponse:
    """Mock HTTP response for testing."""

    def __init__(
        self, status_code: int = 200, json_data: Union[dict[str, Any], None] = None
    ):
        self.status_code = status_code
        self._json_data = json_data or {}

    def json(self) -> dict[str, Any]:
        return self._json_data


def create_mock_places_response(
    places_count: int = 3, fields: Union[list[str], None] = None
) -> MockResponse:
    """
    Create a mock Places API response.

    Args:
        places_count: Number of places to include in response
        fields: Fields to include in each place (defaults to basic fields)

    Returns:
        MockResponse instance
    """
    if fields is None:
        fields = ["displayName.text", "formattedAddress", "types"]

    places = []
    for i in range(places_count):
        place: dict[str, Any] = {}
        if "displayName.text" in fields:
            place["displayName"] = {"text": f"Test Place {i + 1}"}
        if "formattedAddress" in fields:
            place["formattedAddress"] = f"123 Test St, Test City {i + 1}"
        if "types" in fields:
            place["types"] = ["restaurant", "establishment"]
        if "location.latitude" in fields or "location.longitude" in fields:
            place["location"] = {
                "latitude": str(37.7749 + i * 0.001),
                "longitude": str(-122.4194 + i * 0.001),
            }
        places.append(place)

    return MockResponse(200, {"places": places})
