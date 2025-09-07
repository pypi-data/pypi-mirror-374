"""
Tests for Google Places API Nearby Search functionality.

This module contains tests for the nearby search implementation,
including request validation, parameter handling, and API integration.

To run integration tests:
    export GOOGLE_PLACES_API_KEY=your_api_key_here
    pytest -m integration

To run only unit tests:
    pytest -m "not integration"
"""

import os
from typing import Any, TypedDict

import httpx
import pytest
from pydantic import ValidationError

from gmaps import PlacesClient
from gmaps.models import (
    Circle,
    LatLng,
    LocationRestriction,
    NearbySearchRequest,
    RankPreference,
)


class TestNearbySearchRequest:
    """Test cases for NearbySearchRequest model validation."""

    def test_create_basic_request(self):
        """Test creating a basic nearby search request."""
        request = NearbySearchRequest(
            location_restriction=LocationRestriction(
                circle=Circle(
                    center=LatLng(latitude=37.7749, longitude=-122.4194), radius=1000.0
                )
            )
        )

        assert request.location_restriction.circle.center.latitude == 37.7749
        assert request.location_restriction.circle.center.longitude == -122.4194
        assert request.location_restriction.circle.radius == 1000.0
        assert request.max_result_count == 20  # default value
        assert request.rank_preference == RankPreference.POPULARITY  # default value

    def test_create_detailed_request(self):
        """Test creating a detailed nearby search request with all parameters."""
        request = NearbySearchRequest(
            location_restriction=LocationRestriction(
                circle=Circle(
                    center=LatLng(latitude=40.7128, longitude=-74.0060), radius=500.0
                )
            ),
            included_types=["restaurant", "cafe"],
            excluded_types=["fast_food_restaurant"],
            max_result_count=15,
            rank_preference=RankPreference.DISTANCE,
            language_code="en",
            region_code="us",
        )

        assert request.included_types == ["restaurant", "cafe"]
        assert request.excluded_types == ["fast_food_restaurant"]
        assert request.max_result_count == 15
        assert request.rank_preference == RankPreference.DISTANCE
        assert request.language_code == "en"
        assert request.region_code == "us"

    def test_latitude_longitude_validation(self):
        """Test that latitude and longitude are properly validated."""
        # Valid coordinates
        latlng = LatLng(latitude=45.0, longitude=90.0)
        assert latlng.latitude == 45.0
        assert latlng.longitude == 90.0

        # Test boundary values
        LatLng(latitude=90.0, longitude=180.0)  # max values
        LatLng(latitude=-90.0, longitude=-180.0)  # min values

        # Test invalid coordinates should raise validation error
        with pytest.raises(ValidationError):
            LatLng(latitude=91.0, longitude=0.0)  # latitude too high

        with pytest.raises(ValidationError):
            LatLng(latitude=0.0, longitude=181.0)  # longitude too high

    def test_radius_validation(self):
        """Test that circle radius is properly validated."""
        center = LatLng(latitude=0.0, longitude=0.0)

        # Valid radius
        Circle(center=center, radius=1000.0)

        # Test boundary values
        Circle(center=center, radius=1.0)  # minimum valid radius
        Circle(center=center, radius=50000.0)  # maximum valid radius

        # Test invalid radius should raise validation error
        with pytest.raises(ValidationError):
            Circle(center=center, radius=0.0)  # radius too small

        with pytest.raises(ValidationError):
            Circle(center=center, radius=50001.0)  # radius too large

    def test_max_result_count_validation(self):
        """Test that max result count is properly validated."""
        location = LocationRestriction(
            circle=Circle(center=LatLng(latitude=0.0, longitude=0.0), radius=1000.0)
        )

        # Valid counts
        NearbySearchRequest(
            location_restriction=location, max_result_count=1
        )  # minimum
        NearbySearchRequest(
            location_restriction=location, max_result_count=20
        )  # maximum

        # Invalid counts should raise validation error
        with pytest.raises(ValidationError):
            NearbySearchRequest(
                location_restriction=location, max_result_count=0
            )  # too small

        with pytest.raises(ValidationError):
            NearbySearchRequest(
                location_restriction=location, max_result_count=21
            )  # too large

    def test_conflicting_types_validation(self):
        """Test validation of conflicting type restrictions."""
        location = LocationRestriction(
            circle=Circle(center=LatLng(latitude=0.0, longitude=0.0), radius=1000.0)
        )

        with pytest.raises(
            ValidationError, match="Types cannot be both included and excluded"
        ):
            NearbySearchRequest(
                location_restriction=location,
                included_types=["restaurant", "cafe"],
                excluded_types=["restaurant"],
            )

    def test_too_many_types_validation(self):
        """Test validation when too many types are provided."""
        location = LocationRestriction(
            circle=Circle(center=LatLng(latitude=0.0, longitude=0.0), radius=1000.0)
        )

        # Create a list with more than 50 items
        too_many_types = [f"type_{i}" for i in range(51)]

        with pytest.raises(
            ValidationError, match="Type lists cannot contain more than 50 items"
        ):
            NearbySearchRequest(
                location_restriction=location, included_types=too_many_types
            )

    def test_place_type_validation(self):
        """Test validation of place types against allowed constants."""
        location = LocationRestriction(
            circle=Circle(center=LatLng(latitude=0.0, longitude=0.0), radius=1000.0)
        )

        # Valid place types should work
        valid_request = NearbySearchRequest(
            location_restriction=location,
            included_types=["restaurant", "cafe", "museum"],
            excluded_types=["fast_food_restaurant", "gas_station"],
        )
        assert valid_request.included_types == ["restaurant", "cafe", "museum"]
        assert valid_request.excluded_types == ["fast_food_restaurant", "gas_station"]

        # Invalid place types should raise validation error
        with pytest.raises(ValidationError, match="Invalid place type: invalid_type"):
            NearbySearchRequest(
                location_restriction=location,
                included_types=["invalid_type"],
            )

        with pytest.raises(ValidationError, match="Invalid place type: fast_food"):
            NearbySearchRequest(
                location_restriction=location,
                excluded_types=["fast_food"],  # Should be fast_food_restaurant
            )

        with pytest.raises(ValidationError, match="Invalid place type: nonexistent"):
            NearbySearchRequest(
                location_restriction=location,
                included_primary_types=["nonexistent"],
            )

        # Empty strings should also be invalid
        with pytest.raises(
            ValidationError, match="Place types must be non-empty strings"
        ):
            NearbySearchRequest(
                location_restriction=location,
                included_types=["restaurant", ""],
            )

        # Test edge cases with whitespace
        with pytest.raises(
            ValidationError, match="Place types must be non-empty strings"
        ):
            NearbySearchRequest(
                location_restriction=location,
                included_types=["restaurant", "   "],
            )

    def test_request_dict_conversion(self):
        """Test converting request to dictionary for API call."""
        request = NearbySearchRequest(
            location_restriction=LocationRestriction(
                circle=Circle(
                    center=LatLng(latitude=37.7749, longitude=-122.4194), radius=1000.0
                )
            ),
            included_types=["restaurant"],
            max_result_count=10,
            rank_preference=RankPreference.DISTANCE,
        )

        request_dict = request.to_request_dict()

        # Check structure
        assert "locationRestriction" in request_dict
        assert "includedTypes" in request_dict
        assert "maxResultCount" in request_dict
        assert "rankPreference" in request_dict
        assert "circle" in request_dict["locationRestriction"]
        assert "center" in request_dict["locationRestriction"]["circle"]

        # Check values
        center = request_dict["locationRestriction"]["circle"]["center"]
        assert center["latitude"] == 37.7749
        assert center["longitude"] == -122.4194
        assert request_dict["locationRestriction"]["circle"]["radius"] == 1000.0
        assert request_dict["includedTypes"] == ["restaurant"]
        assert request_dict["maxResultCount"] == 10
        assert request_dict["rankPreference"] == "DISTANCE"


@pytest.mark.anyio
class TestPlacesClient:
    """Test cases for PlacesClient initialization and configuration."""

    async def test_client_initialization(self):
        """Test that PlacesClient initializes correctly."""
        PlacesClient()

    async def test_field_mask_validation(self):
        """Test field mask validation in nearby_search method."""
        client = PlacesClient()
        request = NearbySearchRequest(
            location_restriction=LocationRestriction(
                circle=Circle(center=LatLng(latitude=0.0, longitude=0.0), radius=1000.0)
            )
        )

        # Empty field mask should raise error
        with pytest.raises(ValueError, match="field_mask is required"):
            await client.nearby_search(request=request, field_mask="")

        # Also guard against empty list
        with pytest.raises(ValueError, match="field_mask is required"):
            await client.nearby_search(request=request, field_mask=[])

    def test_simple_search_parameters(self):
        """Test the simple search method parameter handling."""
        # This just tests that the method exists and accepts expected parameters
        client = PlacesClient()

        # Test that the method exists and has expected signature
        assert hasattr(client, "nearby_search_simple")
        assert callable(client.nearby_search_simple)


# Integration test fixtures and helpers
@pytest.fixture
def api_key():
    """Get API key from environment, skip test if not available."""
    key = os.getenv("GOOGLE_PLACES_API_KEY")
    if not key:
        pytest.skip("GOOGLE_PLACES_API_KEY environment variable not set")
    return key


@pytest.fixture
def places_client(api_key: str) -> PlacesClient:
    """Create PlacesClient with API key."""
    return PlacesClient(api_key=api_key)


def validate_place_response(
    response_data: dict[str, Any], expected_fields: list[str]
) -> None:
    """Helper to validate Places API response structure."""
    assert "places" in response_data
    assert isinstance(response_data["places"], list)

    if response_data["places"]:  # If we got results
        place = response_data["places"][0]
        for field_path in expected_fields:
            # Handle nested field paths like "displayName.text"
            field_parts = field_path.replace("places.", "").split(".")
            current = place
            for part in field_parts:
                assert part in current, f"Field {part} not found in {current.keys()}"
                current = current[part]


@pytest.mark.integration
class TestNearbySearchIntegration:
    """Integration tests that make real API calls to Google Places."""

    @pytest.mark.asyncio
    async def test_basic_nearby_search_san_francisco(self, places_client):
        """Test basic nearby search for restaurants in San Francisco."""
        async with places_client as client:
            # Search for restaurants near Union Square, San Francisco
            response = await client.nearby_search_simple(
                latitude=37.7875,
                longitude=-122.4083,
                radius=500,
                included_types=["restaurant"],
                max_results=5,
                field_mask=[
                    "places.displayName",
                    "places.formattedAddress",
                    "places.types",
                ],
            )

            # Validate response
            assert response.status_code == 200
            data = response.json()

            validate_place_response(
                data, ["displayName.text", "formattedAddress", "types"]
            )

            # Should find some restaurants
            assert len(data["places"]) > 0

            # All results should include restaurant type
            for place in data["places"]:
                assert "restaurant" in [t.lower() for t in place["types"]]

    @pytest.mark.asyncio
    async def test_detailed_nearby_search_nyc(self, places_client):
        """Test detailed nearby search with full request object in NYC."""
        request = NearbySearchRequest(
            location_restriction=LocationRestriction(
                circle=Circle(
                    center=LatLng(latitude=40.7589, longitude=-73.9851),  # Times Square
                    radius=1000.0,
                )
            ),
            included_types=["restaurant", "cafe"],
            excluded_types=["fast_food_restaurant"],
            max_result_count=10,
            rank_preference=RankPreference.DISTANCE,
            language_code="en",
            region_code="us",
        )

        field_mask = [
            "places.displayName",
            "places.formattedAddress",
            "places.location",
            "places.types",
            "places.rating",
        ]

        async with places_client as client:
            response = await client.nearby_search(
                request=request, field_mask=field_mask
            )

            # Validate response
            assert response.status_code == 200
            data = response.json()

            validate_place_response(
                data,
                [
                    "displayName.text",
                    "formattedAddress",
                    "location.latitude",
                    "location.longitude",
                    "types",
                ],
            )

            # Should find results
            assert len(data["places"]) > 0
            assert len(data["places"]) <= 10  # Respects max results

            # Verify location is within reasonable bounds of Times Square
            for place in data["places"]:
                lat = place["location"]["latitude"]
                lng = place["location"]["longitude"]
                assert 40.75 <= lat <= 40.77  # Rough bounds around Times Square
                assert -74.00 <= lng <= -73.98

    @pytest.mark.asyncio
    async def test_nearby_search_with_ranking(self, places_client):
        """Test nearby search with distance ranking."""
        async with places_client as client:
            # Search for museums near Central Park
            response = await client.nearby_search_simple(
                latitude=40.7829,  # Central Park
                longitude=-73.9654,
                radius=2000,
                included_types=["museum"],
                max_results=5,
                rank_by_distance=True,
                field_mask=["places.displayName", "places.location", "places.types"],
            )

            assert response.status_code == 200
            data = response.json()

            if len(data["places"]) > 1:
                # When ranking by distance, results should be ordered by proximity
                # Calculate distances from search center
                center_lat, center_lng = 40.7829, -73.9654

                distances = []
                for place in data["places"]:
                    lat = place["location"]["latitude"]
                    lng = place["location"]["longitude"]
                    # Simple distance calculation (not geodesic, but good enough for test)
                    dist = ((lat - center_lat) ** 2 + (lng - center_lng) ** 2) ** 0.5
                    distances.append(dist)

                # Verify results are roughly ordered by distance
                # Allow for small variations since Google uses more sophisticated distance calculations
                # than simple Euclidean distance (e.g., geodesic, road distance, etc.)
                sorted_distances = sorted(distances)

                # Check if the ordering is "mostly correct" by allowing small deviations
                # For very close distances (< 0.001 difference), order might vary
                def is_approximately_sorted(
                    actual_distances: list[float], tolerance: float = 0.001
                ) -> bool:
                    for i in range(len(actual_distances) - 1):
                        current = actual_distances[i]
                        next_val = actual_distances[i + 1]
                        # If the difference is significant and they're out of order, fail
                        if next_val < current and (current - next_val) > tolerance:
                            return False
                    return True

                assert is_approximately_sorted(distances), (
                    f"Results should be roughly ordered by distance. "
                    f"Actual: {distances}, Expected (sorted): {sorted_distances}"
                )

    @pytest.mark.asyncio
    async def test_nearby_search_multiple_types(self, places_client):
        """Test nearby search with multiple included types."""
        async with places_client as client:
            # Search for cafes and bakeries in downtown Portland
            response = await client.nearby_search_simple(
                latitude=45.5152,
                longitude=-122.6784,
                radius=800,
                included_types=["cafe", "bakery"],
                max_results=8,
                field_mask=["places.displayName", "places.types", "places.rating"],
            )

            assert response.status_code == 200
            data = response.json()

            # Should find results
            assert len(data["places"]) > 0

            # All results should match one of our included types
            for place in data["places"]:
                place_types = [t.lower() for t in place["types"]]
                assert any(
                    t in place_types for t in ["cafe", "bakery"]
                ), f"Place types {place_types} should include cafe or bakery"

    @pytest.mark.asyncio
    async def test_nearby_search_with_field_mask_variations(self, places_client):
        """Test different field mask configurations."""
        location_params = {
            "latitude": 37.7749,  # San Francisco
            "longitude": -122.4194,
            "radius": 1000,
            "included_types": ["restaurant"],
            "max_results": 3,
        }

        test_cases = [
            # Basic fields
            {
                "field_mask": ["places.displayName"],
                "expected_fields": ["displayName.text"],
            },
            # Multiple fields
            {
                "field_mask": [
                    "places.displayName",
                    "places.formattedAddress",
                    "places.types",
                ],
                "expected_fields": ["displayName.text", "formattedAddress", "types"],
            },
            # Rating and price fields (Enterprise SKU)
            {
                "field_mask": [
                    "places.displayName",
                    "places.rating",
                    "places.priceLevel",
                ],
                "expected_fields": [
                    "displayName.text"
                ],  # rating/price may not always be present
            },
        ]

        async with places_client as client:
            for i, test_case in enumerate(test_cases):
                response = await client.nearby_search_simple(
                    **location_params, field_mask=test_case["field_mask"]
                )

                assert (
                    response.status_code == 200
                ), f"Test case {i} failed with status {response.status_code}"
                data = response.json()

                # Validate basic structure
                assert "places" in data
                if data["places"]:
                    validate_place_response(data, test_case["expected_fields"])

    @pytest.mark.asyncio
    async def test_nearby_search_error_handling(self, api_key):
        """Test error handling with invalid requests."""

        # Test with invalid API key
        invalid_client = PlacesClient(api_key="invalid_key_12345")

        async with invalid_client as client:
            with pytest.raises(httpx.HTTPStatusError):
                await client.nearby_search_simple(
                    latitude=37.7749,
                    longitude=-122.4194,
                    radius=1000,
                    included_types=["restaurant"],
                    max_results=5,
                )

    @pytest.mark.asyncio
    async def test_nearby_search_edge_locations(self, places_client):
        """Test nearby search in various edge case locations."""

        class TestLocation(TypedDict):
            name: str
            latitude: float
            longitude: float
            radius: int
            types: list[str]
            min_results: int

        # Test locations with expected different result characteristics
        test_locations: list[TestLocation] = [
            # Rural location - might have fewer results
            {
                "name": "Rural Montana",
                "latitude": 46.8059,
                "longitude": -110.3626,
                "radius": 10000,  # Larger radius for rural area
                "types": ["gas_station", "restaurant"],
                "min_results": 0,  # Might not find anything
            },
            # Dense urban area - should have many results
            {
                "name": "Manhattan NYC",
                "latitude": 40.7831,
                "longitude": -73.9712,
                "radius": 300,
                "types": ["restaurant"],
                "min_results": 1,  # Should definitely find restaurants
            },
            # International location
            {
                "name": "Tokyo Japan",
                "latitude": 35.6762,
                "longitude": 139.6503,
                "radius": 1000,
                "types": ["restaurant"],
                "min_results": 1,  # Should find restaurants
            },
        ]

        async with places_client as client:
            for location in test_locations:
                response = await client.nearby_search_simple(
                    latitude=location["latitude"],
                    longitude=location["longitude"],
                    radius=location["radius"],
                    included_types=location["types"],
                    max_results=5,
                    field_mask=["places.displayName", "places.formattedAddress"],
                )

                assert response.status_code == 200, f"Failed for {location['name']}"
                data = response.json()

                # Validate structure
                assert "places" in data
                assert (
                    len(data["places"]) >= location["min_results"]
                ), f"{location['name']} should have at least {location['min_results']} results"

    @pytest.mark.asyncio
    async def test_authentication_modes(self):
        """Test different authentication modes."""
        api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        if not api_key:
            pytest.skip("GOOGLE_PLACES_API_KEY not available")

        # Test explicit API key
        async with PlacesClient(api_key=api_key) as client:
            response = await client.nearby_search_simple(
                latitude=37.7749,
                longitude=-122.4194,
                radius=1000,
                included_types=["park"],
                max_results=3,
            )
            assert response.status_code == 200

        # Test auto-detection (API key from environment)
        async with PlacesClient() as client:
            response = await client.nearby_search_simple(
                latitude=37.7749,
                longitude=-122.4194,
                radius=1000,
                included_types=["park"],
                max_results=3,
            )
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_client_configuration(self, api_key):
        """Test client with custom configuration."""
        from gmaps import ClientOptions, RateLimitConfig, RetryConfig

        # Custom configuration
        options = ClientOptions(
            rate_limit=RateLimitConfig(qpm=30),  # Lower rate limit
            retry=RetryConfig(max_attempts=2, backoff_base=0.3),
            timeout=20.0,
            enable_logging=True,
        )

        async with PlacesClient(api_key=api_key, options=options) as client:
            # Verify configuration
            assert client.options.rate_limit.qpm == 30
            assert client.options.retry.max_attempts == 2

            # Make a request to verify it works
            response = await client.nearby_search_simple(
                latitude=40.7128,  # NYC
                longitude=-74.0060,
                radius=800,
                included_types=["tourist_attraction"],
                max_results=3,
            )

            assert response.status_code == 200
            data = response.json()
            assert "places" in data

    @pytest.mark.asyncio
    async def test_large_radius_search(self, places_client):
        """Test search with large radius (marked as slow test)."""
        async with places_client as client:
            # Large radius search around Los Angeles
            response = await client.nearby_search_simple(
                latitude=34.0522,
                longitude=-118.2437,
                radius=25000,  # 25km radius
                included_types=["airport"],
                max_results=10,
                field_mask=[
                    "places.displayName",
                    "places.formattedAddress",
                    "places.types",
                ],
            )

            assert response.status_code == 200
            data = response.json()

            # Should find major airports like LAX
            assert len(data["places"]) > 0

            # All results should be airports
            for place in data["places"]:
                place_types = [t.lower() for t in place["types"]]
                assert "airport" in place_types

    @pytest.mark.asyncio
    async def test_response_caching_and_consistency(self, places_client):
        async def make_request(client: PlacesClient) -> httpx.Response:
            return await client.nearby_search_simple(
                latitude=40.7614,
                longitude=-73.9776,
                radius=500,
                included_types=["restaurant"],
                max_results=5,
                field_mask=["places.displayName", "places.id"],
            )

        async with places_client as client:
            response1 = await make_request(client)
            response2 = await make_request(client)

        assert response1.status_code == 200
        assert response2.status_code == 200

        data1 = response1.json()
        data2 = response2.json()
        assert len(data1["places"]) == len(data2["places"])


if __name__ == "__main__":
    pytest.main([__file__])
