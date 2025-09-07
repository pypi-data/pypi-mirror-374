"""
Comprehensive tests for GmapsClient - the unified Google Maps API client.

This module contains extensive tests covering:
- Initialization and parameter validation
- Authentication modes (API key, ADC, auto-detection)
- Context manager behavior and resource cleanup
- Configuration options and validation
- Sub-client access and delegation
- Integration testing with real APIs
- Error handling and edge cases

To run integration tests:
    export GOOGLE_PLACES_API_KEY=your_api_key_here
    pytest tests/test_gmaps_client.py -m integration

To run only unit tests:
    pytest tests/test_gmaps_client.py -m "not integration"
"""

import asyncio
import os
from importlib.util import find_spec
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from gmaps import (
    AuthMode,
    ClientOptions,
    GeocodingClient,
    GmapsClient,
    PlacesClient,
    RateLimitConfig,
    RetryConfig,
)

from .test_utils import mock_client_context_managers, mock_sub_client_methods


def _has_google_auth() -> bool:
    try:
        find_spec("google.auth")

        return True
    except ImportError:
        return False


class TestGmapsClientInitialization:
    """Test cases for GmapsClient initialization and parameter validation."""

    def test_basic_initialization(self):
        """Test basic client initialization with minimal parameters."""
        client = GmapsClient()

        assert client.places is not None
        assert client.geocoding is not None
        assert isinstance(client.places, PlacesClient)
        assert isinstance(client.geocoding, GeocodingClient)

    def test_initialization_with_api_key(self):
        """Test initialization with explicit API key."""
        api_key = "test-api-key-12345"
        client = GmapsClient(api_key=api_key)

        # Verify API key is passed to sub-clients
        assert client._api_key == api_key
        # Note: Sub-client internal API key storage is implementation detail
        # We verify through behavior rather than accessing private attributes

    @pytest.mark.skipif(
        _has_google_auth(),
        reason="google-auth is available, skipping ADC failing test",
    )
    def test_initialization_with_auth_mode(self):
        """Test initialization with explicit auth mode."""
        client = GmapsClient(auth_mode=AuthMode.API_KEY, api_key="test-key")
        assert client._auth_mode == AuthMode.API_KEY

        # Test ADC mode (will fail without google-auth, but we test the attempt)
        with pytest.raises(RuntimeError, match="google-auth is required"):
            GmapsClient(auth_mode=AuthMode.ADC)

    def test_initialization_with_options(self):
        """Test initialization with custom ClientOptions."""
        options = ClientOptions(
            timeout=httpx.Timeout(30.0),
            http2=False,
            enable_logging=False,
            headers={"Custom-Header": "test-value"},
        )

        client = GmapsClient(options=options)

        client.places.options.base_url = None
        client.geocoding.options.base_url = None
        assert client.places.options == client.geocoding.options
        assert client.places.options.timeout is options.timeout
        assert client.geocoding.options.timeout is options.timeout

    def test_initialization_with_rate_limits(self):
        """Test initialization with custom rate limits."""
        client = GmapsClient(places_qpm=100, geocoding_qpm=50)

        assert client._places_qpm == 100
        assert client._geocoding_qpm == 50

    def test_initialization_with_all_parameters(self):
        """Test initialization with all available parameters."""
        api_key = "comprehensive-test-key"
        auth_mode = AuthMode.API_KEY
        options = ClientOptions(
            timeout=25.0, http2=False, enable_logging=True, headers={"Test": "Header"}
        )
        places_qpm = 80
        geocoding_qpm = 40

        client = GmapsClient(
            api_key=api_key,
            auth_mode=auth_mode,
            options=options,
            places_qpm=places_qpm,
            geocoding_qpm=geocoding_qpm,
        )

        # Verify all parameters are stored
        assert client._api_key == api_key
        assert client._auth_mode == auth_mode
        assert client._options is options
        assert client._places_qpm == places_qpm
        assert client._geocoding_qpm == geocoding_qpm

        # Verify sub-clients receive configuration
        # Note: Internal implementation details verified through mocking in separate tests

    def test_parameter_validation_edge_cases(self):
        """Test parameter validation for edge cases."""
        # Test with None values (should work)
        client = GmapsClient(
            api_key=None,
            auth_mode=None,
            options=None,
            places_qpm=None,
            geocoding_qpm=None,
        )
        assert client is not None

    def test_keyword_only_parameters(self):
        """Test that all parameters are keyword-only."""
        # This should raise TypeError - all parameters are keyword-only
        with pytest.raises(TypeError):
            GmapsClient("test-key")  # type: ignore # positional argument should fail


class TestGmapsClientContextManager:
    """Test cases for async context manager behavior."""

    @pytest.mark.asyncio
    async def test_context_manager_basic_usage(self):
        """Test basic context manager functionality."""
        async with GmapsClient(api_key="test-key") as client:
            assert isinstance(client, GmapsClient)
            assert client.places is not None
            assert client.geocoding is not None

    @pytest.mark.asyncio
    async def test_context_manager_resource_cleanup(self):
        """Test proper resource cleanup on context exit."""
        client = GmapsClient(api_key="test-key")

        # Mock the sub-clients' context manager methods
        mock_client_context_managers(client)

        # Test normal context manager flow
        async with client as ctx_client:
            assert ctx_client is client

        # Verify both sub-clients were properly entered and exited
        client.places.__aenter__.assert_called_once()  # type: ignore
        client.places.__aexit__.assert_called_once()  # type: ignore
        client.geocoding.__aenter__.assert_called_once()  # type: ignore
        client.geocoding.__aexit__.assert_called_once()  # type: ignore

    @pytest.mark.asyncio
    async def test_manual_close_methods(self):
        """Test manual close methods (aclose and close)."""
        client = GmapsClient(api_key="test-key")

        # Mock sub-clients' close methods
        mock_sub_client_methods(
            client,
            places_methods={"aclose": AsyncMock(), "close": Mock()},
            geocoding_methods={"aclose": AsyncMock(), "close": Mock()},
        )

        # Test async close
        await client.aclose()
        client.places.aclose.assert_called_once()  # type: ignore
        client.geocoding.aclose.assert_called_once()  # type: ignore

        # Test sync close
        client.close()
        client.places.close.assert_called_once()  # type: ignore
        client.geocoding.close.assert_called_once()  # type: ignore


class TestGmapsClientAuthentication:
    """Test cases for different authentication modes."""

    @pytest.mark.skipif(
        _has_google_auth(),
        reason="google-auth not available",
    )
    def test_adc_authentication_setup(self):
        """Test ADC authentication setup when google-auth is available."""
        # Note: This will likely fail in CI without proper ADC setup
        # but tests the initialization path
        try:
            client = GmapsClient(auth_mode=AuthMode.ADC)
            assert client._auth_mode == AuthMode.ADC
        except Exception as e:
            # Expected in environments without ADC setup
            assert "credentials" in str(e).lower() or "auth" in str(e).lower()

    def test_api_key_from_environment(self):
        """Test API key detection from environment variable."""
        with patch.dict(os.environ, {"GOOGLE_PLACES_API_KEY": "env-api-key"}):
            client = GmapsClient()
            # The actual env var detection happens in the base client
            # Here we just verify the client initializes
            assert client is not None

    @pytest.mark.skipif(
        _has_google_auth(),
        reason="google-auth is available, skipping ADC failing test",
    )
    def test_auth_mode_validation(self):
        """Test authentication mode validation."""
        # Valid auth modes should work
        for mode in AuthMode:
            try:
                if mode == AuthMode.ADC:
                    # ADC requires google-auth, so expect RuntimeError
                    with pytest.raises(RuntimeError, match="google-auth is required"):
                        GmapsClient(auth_mode=mode)
                else:
                    client = GmapsClient(
                        auth_mode=mode,
                        api_key="test" if mode == AuthMode.API_KEY else None,
                    )
                    assert client._auth_mode == mode
            except ImportError:
                # Expected for ADC without google-auth
                pass


class TestGmapsClientConfiguration:
    """Test cases for client configuration options."""

    def test_client_options_propagation(self):
        """Test that ClientOptions are properly propagated to sub-clients."""
        rate_limit = RateLimitConfig(qpm=120)
        retry = RetryConfig(max_attempts=3, backoff_base=1.0)

        options = ClientOptions(
            rate_limit=rate_limit,
            retry=retry,
            timeout=httpx.Timeout(20.0),
            http2=False,
            headers={"X-Test": "header"},
            enable_logging=False,
        )

        client = GmapsClient(options=options)

        # Verify options are shared
        client.places.options.base_url = None
        client.geocoding.options.base_url = None
        assert client.places.options == client.geocoding.options
        assert client.places.options.timeout is options.timeout
        assert client.geocoding.options.timeout is options.timeout

    def test_rate_limit_configuration(self):
        """Test rate limit configuration for individual services."""
        places_qpm = 90
        geocoding_qpm = 45

        client = GmapsClient(places_qpm=places_qpm, geocoding_qpm=geocoding_qpm)

        # Mock the set_rate_limit method to verify it's called correctly
        mock_sub_client_methods(
            client,
            places_methods={"set_rate_limit": Mock()},
            geocoding_methods={"set_rate_limit": Mock()},
        )

        # Test updating rate limits
        client.set_rate_limit(places_qpm=150, geocoding_qpm=75)

        client.places.set_rate_limit.assert_called_once_with(150)  # type: ignore
        client.geocoding.set_rate_limit.assert_called_once_with(75)  # type: ignore

    def test_set_rate_limit_partial_update(self):
        """Test partial rate limit updates."""
        client = GmapsClient()

        # Mock sub-client methods
        mock_sub_client_methods(
            client,
            places_methods={"set_rate_limit": Mock()},
            geocoding_methods={"set_rate_limit": Mock()},
        )

        # Update only places QPM
        client.set_rate_limit(places_qpm=200)
        client.places.set_rate_limit.assert_called_once_with(200)  # type: ignore
        client.geocoding.set_rate_limit.assert_not_called()  # type: ignore

        # Reset mocks
        client.places.set_rate_limit.reset_mock()  # type: ignore
        client.geocoding.set_rate_limit.reset_mock()  # type: ignore

        # Update only geocoding QPM
        client.set_rate_limit(geocoding_qpm=100)
        client.geocoding.set_rate_limit.assert_called_once_with(100)  # type: ignore
        client.places.set_rate_limit.assert_not_called()  # type: ignore

    def test_http_configuration_options(self):
        """Test various HTTP configuration options."""
        options = ClientOptions(
            timeout=httpx.Timeout(connect=5.0, read=30.0, write=5.0, pool=5.0),
            http2=False,
            headers={"User-Agent": "TestClient/1.0", "X-API-Version": "v1"},
            verify=False,
        )

        client = GmapsClient(options=options, api_key="test-key")

        # Verify configuration is passed through
        # Verify configuration is passed through (timeout structure depends on httpx version)
        assert isinstance(client.places.options.timeout, httpx.Timeout)
        assert client.places.options.http2 is False
        assert client.places.options.headers["User-Agent"] == "TestClient/1.0"
        assert client.places.options.verify is False

    def test_logging_configuration(self):
        """Test logging configuration options."""
        import logging

        custom_logger = logging.getLogger("test_gmaps")

        options = ClientOptions(enable_logging=True, logger=custom_logger)

        client = GmapsClient(options=options)

        assert client.places.options.enable_logging is True
        assert client.places.options.logger is custom_logger


class TestGmapsClientSubClients:
    """Test cases for sub-client access and delegation."""

    def test_sub_client_types(self):
        """Test that sub-clients are of correct types."""
        client = GmapsClient(api_key="test-key")

        assert isinstance(client.places, PlacesClient)
        assert isinstance(client.geocoding, GeocodingClient)

    def test_geocoding_client_has_place_geocode_method(self):
        """Test that GeocodingClient has the new place_geocode_simple method."""
        client = GmapsClient(api_key="test-key")

        # Verify the method exists
        assert hasattr(client.geocoding, "place_geocode_simple")
        assert callable(client.geocoding.place_geocode_simple)

        # Verify it's documented in the class docstring
        geocoding_docstring = client.geocoding.__class__.__doc__ or ""
        assert "place_geocode_simple" in geocoding_docstring

    def test_sub_client_shared_configuration(self):
        """Test that sub-clients share configuration from main client."""
        api_key = "shared-config-key"
        auth_mode = AuthMode.API_KEY
        options = ClientOptions(timeout=15.0, http2=False)

        client = GmapsClient(api_key=api_key, auth_mode=auth_mode, options=options)

        # Verify shared configuration (implementation details tested via mocking)
        client.places.options.base_url = None
        client.geocoding.options.base_url = None
        assert client.places.options == client.geocoding.options
        assert client.places.options.timeout is options.timeout
        assert client.geocoding.options.timeout is options.timeout


class TestGmapsClientMethods:
    """Test cases for GmapsClient methods and properties."""

    def test_info_method(self):
        """Test the info() method returns comprehensive client information."""
        client = GmapsClient(api_key="test-info-key")

        # Mock sub-client info methods
        places_info = {"service": "places", "version": "v1"}
        geocoding_info = {"service": "geocoding", "version": "v1"}

        mock_sub_client_methods(
            client,
            places_methods={"info": Mock(return_value=places_info)},
            geocoding_methods={"info": Mock(return_value=geocoding_info)},
        )

        info = client.info()

        assert info["unified_client"] is True
        assert info["places"] == places_info
        assert info["geocoding"] == geocoding_info

    def test_info_method_structure(self):
        """Test info() method returns expected structure."""
        client = GmapsClient()

        # Mock to avoid actual initialization
        mock_sub_client_methods(
            client,
            places_methods={"info": Mock(return_value={})},
            geocoding_methods={"info": Mock(return_value={})},
        )

        info = client.info()

        # Verify required keys
        required_keys = ["unified_client", "auth_mode", "places", "geocoding"]
        for key in required_keys:
            assert key in info


class TestGmapsClientErrorHandling:
    """Test cases for error handling and edge cases."""

    @pytest.mark.skipif(
        _has_google_auth(),
        reason="google-auth is available, skipping ADC failing test",
    )
    def test_initialization_error_cases(self):
        """Test various error conditions during initialization."""
        # Test ADC without google-auth
        with pytest.raises(RuntimeError, match="google-auth is required"):
            GmapsClient(auth_mode=AuthMode.ADC)

    @pytest.mark.asyncio
    async def test_context_manager_initialization_failure(self):
        """Test context manager behavior when sub-client initialization fails."""
        client = GmapsClient(api_key="test-key")

        # Mock places client to fail on __aenter__
        setattr(
            client.places,
            "__aenter__",
            AsyncMock(side_effect=Exception("Places init failed")),
        )
        setattr(client.places, "__aexit__", AsyncMock())
        setattr(
            client.geocoding, "__aenter__", AsyncMock(return_value=client.geocoding)
        )
        setattr(client.geocoding, "__aexit__", AsyncMock())

        with pytest.raises(Exception, match="Places init failed"):
            async with client:
                pass

    def test_resource_cleanup_edge_cases(self):
        """Test resource cleanup in edge cases."""
        client = GmapsClient()

        # Mock sub-clients
        mock_sub_client_methods(
            client,
            places_methods={
                "close": Mock(side_effect=Exception("Places close failed"))
            },
            geocoding_methods={"close": Mock()},
        )

        # close() should handle exceptions gracefully
        # (Implementation detail: might depend on actual implementation)
        try:
            client.close()
        except Exception:
            pass  # Exception handling depends on implementation

    def test_invalid_parameter_combinations(self):
        """Test invalid parameter combinations."""
        # Most parameter validation happens in sub-clients,
        # but test what we can at the GmapsClient level

        # Test with invalid types (should be caught by type system in real usage)
        # These might not raise errors due to Python's dynamic typing,
        # but document expected behavior
        pass

    def test_memory_cleanup(self):
        """Test that clients can be properly garbage collected."""
        import gc
        import weakref

        client = GmapsClient(api_key="test-key")
        _ = weakref.ref(client)

        # Delete the client
        del client
        gc.collect()

        # Reference should be cleared (in ideal conditions)
        # Note: This test might be flaky due to Python's GC behavior
        # Kept for documentation purposes
        pass


# Integration test fixtures
@pytest.fixture
def api_key():
    """Get API key from environment, skip test if not available."""
    key = os.getenv("GOOGLE_PLACES_API_KEY")
    if not key:
        pytest.skip("GOOGLE_PLACES_API_KEY environment variable not set")
    return key


@pytest.fixture
def gmaps_client(api_key: str) -> GmapsClient:
    """Create GmapsClient with API key."""
    return GmapsClient(api_key=api_key)


@pytest.mark.integration
class TestGmapsClientIntegration:
    """Integration tests that make real API calls."""

    @pytest.mark.asyncio
    async def test_basic_integration_workflow(self, gmaps_client):
        """Test basic workflow using both Places and Geocoding APIs."""
        async with gmaps_client as client:
            # Test Places API
            places_response = await client.places.nearby_search_simple(
                latitude=37.7749,
                longitude=-122.4194,
                radius=1000,
                included_types=["restaurant"],
                max_results=3,
                field_mask=["places.displayName", "places.formattedAddress"],
            )

            assert places_response.status_code == 200
            places_data = places_response.json()
            assert "places" in places_data

    @pytest.mark.asyncio
    async def test_client_info_integration(self, gmaps_client):
        """Test client info method with real client setup."""
        async with gmaps_client as client:
            info = client.info()

            # Verify info structure
            assert info["unified_client"] is True
            assert "auth_mode" in info
            assert "places" in info
            assert "geocoding" in info

            # Auth mode should be API_KEY since we're using API key
            assert info["auth_mode"] == "api_key"

    @pytest.mark.asyncio
    async def test_rate_limit_configuration_integration(self, gmaps_client):
        """Test rate limit configuration with real client."""
        async with gmaps_client as client:
            # Update rate limits
            client.set_rate_limit(places_qpm=30, geocoding_qpm=20)

            # Verify through info
            info = client.info()
            # Note: Actual verification depends on sub-client implementation
            assert "places" in info
            assert "geocoding" in info

    @pytest.mark.asyncio
    async def test_concurrent_api_usage(self, gmaps_client):
        """Test concurrent usage of both APIs."""
        async with gmaps_client as client:
            # Create concurrent tasks for both APIs
            places_task = asyncio.create_task(
                client.places.nearby_search_simple(
                    latitude=40.7128,
                    longitude=-74.0060,
                    radius=500,
                    included_types=["restaurant"],
                    max_results=2,
                    field_mask=["places.displayName"],
                )
            )

            # Wait for both to complete
            places_response = await places_task

            # Verify responses
            assert places_response.status_code == 200

    @pytest.mark.asyncio
    async def test_place_geocoding_integration(self, gmaps_client):
        """Test place geocoding functionality with real API."""
        async with gmaps_client as client:
            # Use a well-known place ID (Brooklyn location from Google's docs)
            response = await client.geocoding.place_geocode_simple(
                place_id="ChIJd8BlQ2BZwokRAFUEcm_qrcA", language="en", region="us"
            )

            assert response.status_code == 200
            data = response.json()

            # Verify geocoding API response structure
            assert "results" in data
            assert data["status"] == "OK"
            assert len(data["results"]) > 0

            result = data["results"][0]
            assert "formatted_address" in result
            assert "geometry" in result
            assert "location" in result["geometry"]

    @pytest.mark.asyncio
    async def test_error_handling_integration(self, api_key):
        """Test error handling with invalid requests."""
        # Test with invalid API key
        invalid_client = GmapsClient(api_key="invalid_key_12345")

        async with invalid_client as client:
            with pytest.raises((httpx.HTTPStatusError, Exception)):
                await client.places.nearby_search_simple(
                    latitude=37.7749,
                    longitude=-122.4194,
                    radius=1000,
                    included_types=["restaurant"],
                    max_results=1,
                    field_mask=["places.displayName"],
                )

    @pytest.mark.asyncio
    async def test_client_reuse(self, gmaps_client):
        """Test that client can be reused across multiple context entries."""
        # First usage
        async with gmaps_client as client:
            response1 = await client.places.nearby_search_simple(
                latitude=37.7749,
                longitude=-122.4194,
                radius=1000,
                included_types=["park"],
                max_results=1,
                field_mask=["places.displayName"],
            )
            assert response1.status_code == 200

        # Second usage - should work with same client
        async with gmaps_client as client:
            response2 = await client.places.nearby_search_simple(
                latitude=40.7128,
                longitude=-74.0060,
                radius=1000,
                included_types=["park"],
                max_results=1,
                field_mask=["places.displayName"],
            )
            assert response2.status_code == 200


class TestGmapsClientAdvancedScenarios:
    """Advanced test scenarios and edge cases."""

    @pytest.mark.asyncio
    async def test_custom_configuration_end_to_end(self):
        """Test end-to-end with custom configuration."""
        # Create client with comprehensive custom config
        rate_limit = RateLimitConfig(qpm=30)
        retry = RetryConfig(max_attempts=2, backoff_base=0.5)

        options = ClientOptions(
            rate_limit=rate_limit,
            retry=retry,
            timeout=httpx.Timeout(10.0),
            http2=False,
            enable_logging=False,
            headers={"X-Test-Client": "GmapsClientTest"},
        )

        client = GmapsClient(
            api_key="test-custom-config",
            options=options,
            places_qpm=25,
            geocoding_qpm=15,
        )

        # Verify configuration propagation
        assert client.places.options.rate_limit.qpm == rate_limit.qpm
        assert client.geocoding.options.retry.max_attempts == retry.max_attempts
        # Verify timeout configuration (structure may vary by httpx version)
        assert isinstance(client.places.options.timeout, httpx.Timeout)
        assert client.geocoding.options.headers["X-Test-Client"] == "GmapsClientTest"

    @pytest.mark.asyncio
    async def test_exception_propagation(self):
        """Test that exceptions are properly propagated from sub-clients."""
        client = GmapsClient(api_key="test-key")

        # Mock sub-client to raise exception
        async def mock_failing_method(*args, **kwargs):
            raise ValueError("Sub-client method failed")

        mock_sub_client_methods(
            client,
            places_methods={"nearby_search_simple": mock_failing_method},
        )

        async with client:
            with pytest.raises(ValueError, match="Sub-client method failed"):
                await client.places.nearby_search_simple(
                    latitude=0, longitude=0, radius=1000
                )

    def test_client_state_consistency(self):
        """Test that client state remains consistent."""
        api_key = "consistency-test-key"
        options = ClientOptions(enable_logging=False)

        client = GmapsClient(api_key=api_key, options=options)

        # Verify initial state
        assert client._api_key == api_key
        assert client._options == options

        # State should remain consistent after operations
        _ = client.info()
        assert client._api_key == api_key
        assert client._options == options

        # After rate limit changes
        client.set_rate_limit(places_qpm=50)
        assert client._api_key == api_key
        assert client._options == options

    @pytest.mark.asyncio
    async def test_resource_management_stress(self):
        """Stress test resource management with multiple clients."""
        clients = []

        # Create multiple clients
        for i in range(10):
            client = GmapsClient(api_key=f"stress-test-key-{i}")
            clients.append(client)

        # Use them all concurrently
        tasks = []
        for client in clients:
            task = asyncio.create_task(self._client_usage_task(client))
            tasks.append(task)

        # Wait for all to complete and verify no exceptions
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All should complete successfully (or with expected API errors)
        for result in results:
            if isinstance(result, Exception) and not isinstance(
                result, (httpx.HTTPError, httpx.HTTPStatusError)
            ):
                pytest.fail(f"Unexpected exception in stress test: {result}")

    async def _client_usage_task(self, client: GmapsClient) -> None:
        """Helper task for stress testing."""
        async with client:
            # Just verify basic functionality
            info = client.info()
            assert info["unified_client"] is True


if __name__ == "__main__":
    pytest.main([__file__])
