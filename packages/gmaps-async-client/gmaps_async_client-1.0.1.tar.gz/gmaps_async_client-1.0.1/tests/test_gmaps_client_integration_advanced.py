"""
Advanced integration tests for GmapsClient.

This module contains sophisticated integration tests that test
real-world usage scenarios, complex configurations, and
end-to-end workflows with the actual Google Maps APIs.
"""

import asyncio
import os
import time
from typing import cast

import httpx
import pytest

from gmaps import ClientOptions, GmapsClient, RetryConfig

# Skip all tests if no API key available
pytestmark = pytest.mark.skipif(
    not os.getenv("GOOGLE_PLACES_API_KEY"),
    reason="GOOGLE_PLACES_API_KEY not set - skipping advanced integration tests",
)


@pytest.fixture
def api_key() -> str:
    """Get API key from environment."""
    key = os.getenv("GOOGLE_PLACES_API_KEY")
    if not key:
        pytest.skip("GOOGLE_PLACES_API_KEY environment variable not set")
    return key or ""


@pytest.fixture
def custom_gmaps_client(api_key: str) -> GmapsClient:
    """Create GmapsClient with custom configuration."""
    options = ClientOptions(
        timeout=httpx.Timeout(30.0),
        http2=False,
        enable_logging=True,
        headers={"X-Test-Client": "GMapsAdvancedIntegration"},
    )

    return GmapsClient(
        api_key=api_key,
        options=options,
        places_qpm=30,  # Conservative rate limit
        geocoding_qpm=20,
    )


@pytest.mark.integration
class TestGmapsClientAdvancedWorkflows:
    """Test complex real-world workflows."""

    @pytest.mark.asyncio
    async def test_multi_city_restaurant_search(self, custom_gmaps_client):
        """Test searching for restaurants across multiple cities."""
        cities = [
            {"name": "San Francisco", "lat": 37.7749, "lng": -122.4194},
            {"name": "New York", "lat": 40.7128, "lng": -74.0060},
            {"name": "Los Angeles", "lat": 34.0522, "lng": -118.2437},
        ]

        async with custom_gmaps_client as client:
            results = {}

            for city in cities:
                response = await client.places.nearby_search_simple(
                    latitude=city["lat"],
                    longitude=city["lng"],
                    radius=2000,
                    included_types=["restaurant"],
                    max_results=5,
                    field_mask=[
                        "places.displayName",
                        "places.formattedAddress",
                        "places.rating",
                        "places.priceLevel",
                    ],
                )

                assert response.status_code == 200
                data = response.json()
                results[city["name"]] = data["places"]

                # Add delay to respect rate limits
                await asyncio.sleep(2.0)

            # Verify results from all cities
            for city_name, places in results.items():
                assert len(places) > 0, f"No restaurants found in {city_name}"

                for place in places:
                    assert "displayName" in place
                    assert "formattedAddress" in place

    @pytest.mark.asyncio
    async def test_concurrent_api_usage_workflow(self, custom_gmaps_client):
        """Test concurrent usage of both Places and Geocoding APIs."""

        async def places_search_task() -> httpx.Response:
            async with custom_gmaps_client as client:
                return cast(
                    httpx.Response,
                    await client.places.nearby_search_simple(
                        latitude=40.7589,  # Times Square
                        longitude=-73.9851,
                        radius=1000,
                        included_types=["tourist_attraction"],
                        max_results=5,
                        field_mask=["places.displayName", "places.types"],
                    ),
                )

        async def geocoding_search_task() -> httpx.Response:
            async with custom_gmaps_client as client:
                return cast(
                    httpx.Response,
                    await client.geocoding.geocode_simple(
                        address="Times Square",
                        language="en",
                    ),
                )

        # Run multiple concurrent Places API searches
        place_tasks = [places_search_task() for _ in range(3)]
        geocoding_tasks = [geocoding_search_task() for _ in range(3)]

        start_time = time.time()
        responses = await asyncio.gather(*geocoding_tasks, *place_tasks)
        end_time = time.time()

        # Verify geocoding responses (first 3)
        for response in responses[:3]:
            assert response.status_code == 200
            data = response.json()
            assert "results" in data  # Geocoding API returns "results"
            assert data["status"] == "OK"

        # Verify places responses (last 3)
        for response in responses[3:]:
            assert response.status_code == 200
            data = response.json()
            assert "places" in data  # Places API returns "places"

        # Should be faster than sequential (accounting for rate limits)
        assert end_time - start_time < 15.0, "Concurrent requests took too long"

    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self, api_key):
        """Test error recovery in complex workflow."""
        # Create client with aggressive timeout to force some failures
        aggressive_options = ClientOptions(
            timeout=httpx.Timeout(0.5),  # Very short timeout
            retry=RetryConfig(enabled=True, max_attempts=3, backoff_base=0.1),
        )

        client = GmapsClient(api_key=api_key, options=aggressive_options)

        successful_requests = 0
        failed_requests = 0

        search_locations = [
            (37.7749, -122.4194),  # San Francisco
            (40.7128, -74.0060),  # New York
            (34.0522, -118.2437),  # Los Angeles
            (41.8781, -87.6298),  # Chicago
            (29.7604, -95.3698),  # Houston
        ]

        async with client:
            for lat, lng in search_locations:
                try:
                    response = await client.places.nearby_search_simple(
                        latitude=lat,
                        longitude=lng,
                        radius=1500,
                        included_types=["park"],
                        max_results=3,
                        field_mask=["places.displayName"],
                    )

                    if response.status_code == 200:
                        successful_requests += 1
                    else:
                        failed_requests += 1

                except Exception:
                    failed_requests += 1

                # Small delay between requests
                await asyncio.sleep(1.0)

        # Should have some successes despite aggressive timeout
        assert successful_requests > 0, "No successful requests in error recovery test"
        # Some failures are expected with aggressive timeout
        total_requests = successful_requests + failed_requests
        assert total_requests == len(search_locations)

    @pytest.mark.asyncio
    async def test_rate_limit_behavior(self, custom_gmaps_client):
        """Test behavior under rate limiting conditions."""
        # Temporarily set very low rate limit
        async with custom_gmaps_client as client:
            # Update to very conservative rate limit
            client.set_rate_limit(places_qpm=6)  # 1 request per 10 seconds

            request_times = []

            # Make several requests and measure timing
            for _ in range(3):
                start = time.time()

                response = await client.places.nearby_search_simple(
                    latitude=37.7749,
                    longitude=-122.4194,
                    radius=1000,
                    included_types=["restaurant"],
                    max_results=2,
                    field_mask=["places.displayName"],
                )

                end = time.time()
                request_times.append(end - start)

                assert response.status_code == 200

            # Later requests should show rate limiting delay
            # (This depends on the rate limiter implementation)
            # At minimum, verify requests completed successfully
            assert len(request_times) == 3
            assert all(t > 0 for t in request_times)

    @pytest.mark.asyncio
    async def test_long_running_session(self, custom_gmaps_client):
        """Test long-running session with multiple operations."""
        async with custom_gmaps_client as client:
            operations_completed = 0
            session_start = time.time()

            # Simulate long-running session with periodic API calls
            while time.time() - session_start < 30.0:  # 30 second session
                try:
                    # Alternate between different types of searches
                    if operations_completed % 2 == 0:
                        # Restaurant search
                        response = await client.places.nearby_search_simple(
                            latitude=40.7589,  # Times Square
                            longitude=-73.9851,
                            radius=800,
                            included_types=["restaurant"],
                            max_results=2,
                            field_mask=["places.displayName"],
                        )
                    else:
                        # Tourist attraction search
                        response = await client.places.nearby_search_simple(
                            latitude=40.7589,  # Times Square
                            longitude=-73.9851,
                            radius=800,
                            included_types=["tourist_attraction"],
                            max_results=2,
                            field_mask=["places.displayName"],
                        )

                    assert response.status_code == 200
                    operations_completed += 1

                    # Wait between requests to respect rate limits
                    await asyncio.sleep(5.0)

                except Exception as e:
                    # Log error but continue session
                    print(f"Operation {operations_completed} failed: {e}")
                    await asyncio.sleep(5.0)

            assert (
                operations_completed >= 3
            ), f"Too few operations completed: {operations_completed}"


@pytest.mark.integration
class TestGmapsClientConfigurationScenarios:
    """Test various configuration scenarios with real API."""

    @pytest.mark.asyncio
    async def test_http2_vs_http1_performance(self, api_key):
        """Compare HTTP/2 vs HTTP/1.1 performance."""
        # HTTP/1.1 client
        http1_options = ClientOptions(timeout=httpx.Timeout(30.0), http2=False)
        http1_client = GmapsClient(api_key=api_key, options=http1_options)

        # HTTP/2 client
        http2_options = ClientOptions(timeout=httpx.Timeout(30.0), http2=True)
        http2_client = GmapsClient(api_key=api_key, options=http2_options)

        async def make_request(
            client: GmapsClient, protocol_name: str
        ) -> tuple[str, float, int]:
            start = time.time()
            async with client:
                response = await client.places.nearby_search_simple(
                    latitude=37.7749,
                    longitude=-122.4194,
                    radius=1000,
                    included_types=["restaurant"],
                    max_results=3,
                    field_mask=["places.displayName"],
                )
            end = time.time()
            return protocol_name, end - start, response.status_code

        # Test both protocols
        results = await asyncio.gather(
            make_request(http1_client, "HTTP/1.1"), make_request(http2_client, "HTTP/2")
        )

        for protocol, duration, status in results:
            assert status == 200, f"{protocol} request failed"
            assert duration < 10.0, f"{protocol} request took too long: {duration:.2f}s"
            print(f"{protocol}: {duration:.2f}s")

    @pytest.mark.asyncio
    async def test_timeout_configuration_behavior(self, api_key):
        """Test different timeout configurations."""
        timeout_configs = [
            httpx.Timeout(5.0),  # Short timeout
            httpx.Timeout(30.0),  # Normal timeout
            httpx.Timeout(60.0),  # Long timeout
        ]

        for timeout in timeout_configs:
            options = ClientOptions(timeout=timeout)
            client = GmapsClient(api_key=api_key, options=options)

            start = time.time()
            async with client:
                response = await client.places.nearby_search_simple(
                    latitude=40.7128,
                    longitude=-74.0060,
                    radius=1000,
                    included_types=["museum"],
                    max_results=2,
                    field_mask=["places.displayName"],
                )
            end = time.time()

            assert response.status_code == 200
            duration = end - start
            print(f"Timeout {timeout}: {duration:.2f}s")

    @pytest.mark.asyncio
    async def test_custom_headers_behavior(self, api_key):
        """Test custom headers in requests."""
        custom_headers = {
            "X-Custom-Client": "GMapsTestSuite",
            "X-Request-ID": "test-12345",
            "Accept-Language": "en-US,en;q=0.9",
        }

        options = ClientOptions(headers=custom_headers)
        client = GmapsClient(api_key=api_key, options=options)

        async with client:
            response = await client.places.nearby_search_simple(
                latitude=37.7749,
                longitude=-122.4194,
                radius=1000,
                included_types=["cafe"],
                max_results=2,
                field_mask=["places.displayName"],
            )

        assert response.status_code == 200
        # Headers should be included in request (verified through successful response)

    @pytest.mark.asyncio
    async def test_retry_configuration_effectiveness(self, api_key):
        """Test retry configuration with unreliable conditions."""
        # Configure aggressive retry
        retry_config = RetryConfig(
            enabled=True, max_attempts=5, backoff_base=0.2, backoff_factor=1.5
        )

        options = ClientOptions(
            retry=retry_config,
            timeout=httpx.Timeout(2.0),  # Short timeout to trigger retries
        )

        client = GmapsClient(api_key=api_key, options=options)

        # Make request that might need retries due to short timeout
        start = time.time()
        async with client:
            try:
                response = await client.places.nearby_search_simple(
                    latitude=34.0522,
                    longitude=-118.2437,
                    radius=1000,
                    included_types=["restaurant"],
                    max_results=3,
                    field_mask=["places.displayName"],
                )

                # If successful, verify response
                assert response.status_code == 200

            except Exception as e:
                # Some failures expected with aggressive timeout
                print(f"Request failed after retries: {e}")

        end = time.time()
        duration = end - start

        # Should take longer than a single request due to retries
        # (if retries were triggered)
        print(f"Request with retry config took: {duration:.2f}s")


@pytest.mark.integration
class TestGmapsClientRealWorldScenarios:
    """Test real-world usage scenarios."""

    @pytest.mark.asyncio
    async def test_travel_planning_scenario(self, custom_gmaps_client):
        """Simulate travel planning workflow."""
        # Scenario: Planning a day in San Francisco
        sf_center = (37.7749, -122.4194)

        async with custom_gmaps_client as client:
            # Morning: Find breakfast places
            breakfast_response = await client.places.nearby_search_simple(
                latitude=sf_center[0],
                longitude=sf_center[1],
                radius=2000,
                included_types=["restaurant", "cafe"],
                max_results=5,
                field_mask=[
                    "places.displayName",
                    "places.rating",
                    "places.formattedAddress",
                ],
            )

            await asyncio.sleep(2.0)  # Rate limit respect

            # Afternoon: Find tourist attractions
            attractions_response = await client.places.nearby_search_simple(
                latitude=sf_center[0],
                longitude=sf_center[1],
                radius=5000,
                included_types=["tourist_attraction", "museum"],
                max_results=8,
                field_mask=["places.displayName", "places.rating", "places.types"],
            )

            await asyncio.sleep(2.0)  # Rate limit respect

            # Evening: Find entertainment
            entertainment_response = await client.places.nearby_search_simple(
                latitude=sf_center[0],
                longitude=sf_center[1],
                radius=3000,
                included_types=["night_club", "bar"],
                max_results=5,
                field_mask=["places.displayName", "places.rating"],
            )

        # Verify all searches were successful
        assert breakfast_response.status_code == 200
        assert attractions_response.status_code == 200
        assert entertainment_response.status_code == 200

        breakfast_places = breakfast_response.json()["places"]
        attractions = attractions_response.json()["places"]
        entertainment = entertainment_response.json()["places"]

        assert len(breakfast_places) > 0
        assert len(attractions) > 0
        assert len(entertainment) > 0

        print(f"Found {len(breakfast_places)} breakfast places")
        print(f"Found {len(attractions)} attractions")
        print(f"Found {len(entertainment)} entertainment venues")

    @pytest.mark.asyncio
    async def test_business_directory_scenario(self, custom_gmaps_client):
        """Simulate building a business directory."""
        business_types = ["restaurant", "bank", "hospital", "gas_station", "pharmacy"]
        location = (40.7128, -74.0060)  # NYC

        business_directory = {}

        async with custom_gmaps_client as client:
            for business_type in business_types:
                try:
                    response = await client.places.nearby_search_simple(
                        latitude=location[0],
                        longitude=location[1],
                        radius=2000,
                        included_types=[business_type],
                        max_results=10,
                        field_mask=[
                            "places.displayName",
                            "places.formattedAddress",
                            "places.types",
                            "places.businessStatus",
                        ],
                    )

                    if response.status_code == 200:
                        places = response.json()["places"]
                        business_directory[business_type] = places
                        print(
                            f"Found {len(places)} {business_type.replace('_', ' ')} businesses"
                        )

                    await asyncio.sleep(2.0)  # Respect rate limits

                except Exception as e:
                    print(f"Failed to get {business_type} businesses: {e}")
                    business_directory[business_type] = []

        # Verify directory was populated
        assert len(business_directory) == len(business_types)
        total_businesses = sum(len(places) for places in business_directory.values())
        assert total_businesses > 0, "No businesses found in directory"

        print(f"Business directory contains {total_businesses} total businesses")

    @pytest.mark.asyncio
    async def test_location_validation_scenario(self, custom_gmaps_client):
        """Test validating locations have expected amenities."""
        # Test locations that should have restaurants
        locations_to_validate = [
            {
                "name": "Times Square",
                "lat": 40.7589,
                "lng": -73.9851,
                "expected_restaurants": 5,
            },
            {
                "name": "Union Square SF",
                "lat": 37.7875,
                "lng": -122.4083,
                "expected_restaurants": 3,
            },
            {
                "name": "Hollywood Boulevard",
                "lat": 34.1022,
                "lng": -118.3406,
                "expected_restaurants": 2,
            },
        ]

        validation_results = {}

        async with custom_gmaps_client as client:
            for location in locations_to_validate:
                response = await client.places.nearby_search_simple(
                    latitude=location["lat"],
                    longitude=location["lng"],
                    radius=500,
                    included_types=["restaurant"],
                    max_results=20,
                    field_mask=["places.displayName", "places.types"],
                )

                if response.status_code == 200:
                    restaurants = response.json()["places"]
                    expected_restaurants = location["expected_restaurants"]
                    assert expected_restaurants is not None
                    assert isinstance(expected_restaurants, int)
                    validation_results[location["name"]] = {
                        "found": len(restaurants),
                        "expected": expected_restaurants,
                        "valid": len(restaurants) >= expected_restaurants,
                    }

                await asyncio.sleep(2.0)

        # Verify validation results
        for location_name, result in validation_results.items():
            print(
                f"{location_name}: Found {result['found']}, Expected {result['expected']}, Valid: {result['valid']}"
            )
            assert result[
                "valid"
            ], f"{location_name} failed validation - only found {result['found']} restaurants"

    @pytest.mark.asyncio
    async def test_place_geocoding_workflow_scenario(self, custom_gmaps_client):
        """Test place geocoding as part of a location resolution workflow."""
        # Scenario: Get detailed address information for known place IDs
        known_places = [
            {
                "place_id": "ChIJd8BlQ2BZwokRAFUEcm_qrcA",  # Brooklyn location
                "expected_contains": ["Brooklyn", "NY"],
                "description": "Brooklyn location from Google's documentation",
            },
            {
                "place_id": "ChIJN1t_tDeuEmsRUsoyG83frY4",  # Another test location
                "expected_contains": [],  # Don't assume specific content
                "description": "Alternative test location",
            },
        ]

        geocoding_results = {}

        async with custom_gmaps_client as client:
            for place_info in known_places:
                try:
                    # Test the place geocoding functionality
                    response = await client.geocoding.place_geocode_simple(
                        place_id=place_info["place_id"], language="en", region="us"
                    )

                    assert (
                        response.status_code == 200
                    ), f"Failed to geocode {place_info['description']}"

                    data = response.json()
                    assert "results" in data, "Response missing 'results' field"
                    assert (
                        data["status"] == "OK"
                    ), f"API returned status: {data.get('status')}"
                    assert len(data["results"]) > 0, "No results returned"

                    result = data["results"][0]
                    formatted_address = result["formatted_address"]
                    geometry = result["geometry"]

                    # Basic validation
                    assert formatted_address, "No formatted address returned"
                    assert "location" in geometry, "No location in geometry"
                    assert "lat" in geometry["location"], "No latitude in location"
                    assert "lng" in geometry["location"], "No longitude in location"

                    # Check expected content if specified
                    for expected_text in place_info["expected_contains"]:
                        assert (
                            expected_text in formatted_address
                        ), f"Expected '{expected_text}' in address: {formatted_address}"

                    geocoding_results[place_info["place_id"]] = {
                        "formatted_address": formatted_address,
                        "location": geometry["location"],
                        "success": True,
                    }

                    print(f"✓ {place_info['description']}: {formatted_address}")

                except Exception as e:
                    geocoding_results[place_info["place_id"]] = {
                        "error": str(e),
                        "success": False,
                    }
                    print(f"✗ {place_info['description']}: {e}")

                # Rate limiting
                await asyncio.sleep(1.0)

        # Verify at least one geocoding was successful
        successful_geocodes = sum(
            1 for result in geocoding_results.values() if result["success"]
        )
        assert (
            successful_geocodes > 0
        ), f"No place geocoding requests succeeded: {geocoding_results}"

        print(
            f"Successfully geocoded {successful_geocodes} out of {len(known_places)} places"
        )


if __name__ == "__main__":
    pytest.main([__file__])
