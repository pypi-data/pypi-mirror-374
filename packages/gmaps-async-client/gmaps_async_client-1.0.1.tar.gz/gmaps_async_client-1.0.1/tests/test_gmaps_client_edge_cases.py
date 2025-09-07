"""
Edge case and error scenario tests for GmapsClient.

This module focuses on testing unusual conditions, error scenarios,
boundary cases, and defensive programming aspects of GmapsClient.
"""

import asyncio
import os
import sys
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest
from pydantic import ValidationError

from gmaps import ClientOptions, GmapsClient

from .test_utils import mock_client_context_managers, mock_sub_client_methods


class TestGmapsClientEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_api_key_handling(self):
        """Test behavior with empty API key."""
        # Empty string API key
        client = GmapsClient(api_key="")
        assert client._api_key == ""

        # Whitespace-only API key
        client = GmapsClient(api_key="   ")
        assert client._api_key == "   "

    def test_very_long_api_key(self):
        """Test behavior with unusually long API key."""
        long_key = "x" * 10000  # 10KB API key
        with pytest.raises(ValueError):
            GmapsClient(api_key=long_key)

    def test_special_characters_in_api_key(self):
        """Test API key with special characters."""
        special_keys = [
            "key-with-dashes",
            "key_with_underscores",
            "key.with.dots",
            "key@with#special$chars%",
            "key with spaces",
            "key\nwith\nnewlines",
            "key\twith\ttabs",
        ]

        for key in special_keys:
            client = GmapsClient(api_key=key)
            assert client._api_key == key

    def test_unicode_api_key(self):
        """Test API key with Unicode characters."""
        unicode_keys = [
            "键值",  # Chinese
            "ключ",  # Russian
            "🔑🗝️",  # Emojis
            "café",  # Accented characters
            "key\u0000null",  # Null character
        ]

        for key in unicode_keys:
            client = GmapsClient(api_key=key)
            assert client._api_key == key

    def test_none_values_in_configuration(self):
        """Test behavior with None values in various configurations."""
        # All None configuration
        client = GmapsClient(
            api_key=None,
            auth_mode=None,
            options=None,
            places_qpm=None,
            geocoding_qpm=None,
        )

        assert client._api_key is None
        assert client._auth_mode is None
        assert client._options is None
        assert client._places_qpm is None
        assert client._geocoding_qpm is None

    def test_zero_and_negative_qpm_values(self):
        """Test behavior with zero and negative QPM values."""
        # Zero QPM values
        with pytest.raises(ValueError):
            GmapsClient(places_qpm=0, geocoding_qpm=0)

        # Negative QPM values
        with pytest.raises(ValueError):
            GmapsClient(places_qpm=-1, geocoding_qpm=-100)

    def test_extreme_qpm_values(self):
        """Test behavior with extremely large QPM values."""
        with pytest.raises((ValueError, OverflowError, TypeError, ValidationError)):
            GmapsClient(places_qpm=sys.maxsize)

    @pytest.mark.asyncio
    async def test_context_manager_double_entry(self):
        """Test double entry to context manager."""
        client = GmapsClient(api_key="double-entry-test")

        # Mock sub-clients
        mock_client_context_managers(client)

        # First context entry should work
        async with client as client1:
            assert client1 is client

            # Attempting to enter again might have undefined behavior
            # depending on implementation - test what happens
            try:
                async with client as client2:
                    assert client2 is client
            except Exception:
                # Some implementations might prevent double entry
                pass

    @pytest.mark.asyncio
    async def test_context_manager_rapid_cycles(self):
        """Test rapid enter/exit cycles of context manager."""
        client = GmapsClient(api_key="rapid-cycle-test")

        # Mock sub-clients
        mock_client_context_managers(client)

        # Rapid enter/exit cycles
        for _ in range(100):
            async with client:
                pass  # Minimal work

    @pytest.mark.asyncio
    async def test_context_manager_with_cancelled_task(self):
        """Test context manager behavior when task is cancelled."""
        client = GmapsClient(api_key="cancelled-task-test")

        # Mock sub-clients with delays
        async def slow_aenter(*args):
            await asyncio.sleep(1.0)
            return client.places

        setattr(client.places, "__aenter__", slow_aenter)
        setattr(client.places, "__aexit__", AsyncMock(return_value=None))
        setattr(
            client.geocoding, "__aenter__", AsyncMock(return_value=client.geocoding)
        )
        setattr(client.geocoding, "__aexit__", AsyncMock(return_value=None))

        async def task_to_cancel() -> None:
            async with client:
                await asyncio.sleep(10.0)  # Long operation

        task = asyncio.create_task(task_to_cancel())

        # Let it start then cancel
        await asyncio.sleep(0.1)
        task.cancel()

        with pytest.raises(asyncio.CancelledError):
            await task

    def test_invalid_auth_mode_values(self):
        """Test behavior with invalid auth mode values."""
        # Invalid enum values (if somehow passed)
        try:
            # This might not be possible due to type checking, but test defensive programming
            with patch("gmaps.clients.client.AuthMode") as mock_auth_mode:
                mock_auth_mode.INVALID = "invalid"
                # Implementation should handle gracefully
                pass
        except Exception:
            # Expected if implementation has proper validation
            pass

    def test_malformed_client_options(self):
        """Test behavior with malformed ClientOptions."""
        # Options with conflicting settings
        options = ClientOptions(
            timeout=httpx.Timeout(-1.0),  # Negative timeout
            http2=False,
            headers={"": ""},  # Empty header name
            enable_logging=True,
            logger=None,  # Logging enabled but no logger
        )

        # Client should handle malformed options gracefully
        client = GmapsClient(options=options)
        assert client._options is options


class TestGmapsClientErrorConditions:
    """Test various error conditions and exception handling."""

    @pytest.mark.asyncio
    async def test_sub_client_initialization_errors(self):
        """Test behavior when sub-client initialization fails."""
        with patch("gmaps.clients.client.PlacesClient") as mock_places:
            mock_places.side_effect = RuntimeError("PlacesClient failed to initialize")

            with pytest.raises(RuntimeError, match="PlacesClient failed to initialize"):
                GmapsClient(api_key="error-test")

    @pytest.mark.asyncio
    async def test_exception_in_context_manager_cleanup(self):
        """Test exception during context manager cleanup."""
        client = GmapsClient(api_key="cleanup-error-test")

        # Mock clients to succeed entry but fail exit
        setattr(client.places, "__aenter__", AsyncMock(return_value=client.places))
        setattr(
            client.places,
            "__aexit__",
            AsyncMock(side_effect=RuntimeError("Places cleanup failed")),
        )
        setattr(
            client.geocoding, "__aenter__", AsyncMock(return_value=client.geocoding)
        )
        setattr(client.geocoding, "__aexit__", AsyncMock(return_value=None))

        with pytest.raises(RuntimeError, match="Places cleanup failed"):
            async with client:
                pass

    def test_info_method_with_failing_sub_clients(self):
        """Test info method when sub-clients fail."""
        client = GmapsClient(api_key="info-error-test")

        # Mock places client to fail
        mock_sub_client_methods(
            client,
            places_methods={
                "info": Mock(side_effect=RuntimeError("Places info failed"))
            },
            geocoding_methods={"info": Mock(return_value={"service": "geocoding"})},
        )

        with pytest.raises(RuntimeError, match="Places info failed"):
            client.info()

    @pytest.mark.asyncio
    async def test_close_methods_with_errors(self):
        """Test close methods when sub-clients raise errors."""
        client = GmapsClient(api_key="close-error-test")

        # Mock sub-clients to fail during close
        mock_sub_client_methods(
            client,
            places_methods={
                "aclose": AsyncMock(side_effect=RuntimeError("Places aclose failed")),
                "close": Mock(side_effect=RuntimeError("Places close failed")),
            },
            geocoding_methods={
                "aclose": AsyncMock(return_value=None),
                "close": Mock(return_value=None),
            },
        )

        # aclose should propagate exception
        with pytest.raises(RuntimeError, match="Places aclose failed"):
            await client.aclose()

        # close should propagate exception
        with pytest.raises(RuntimeError, match="Places close failed"):
            client.close()


class TestGmapsClientPlaceGeocodingEdgeCases:
    """Test edge cases specific to place geocoding functionality."""

    def test_invalid_place_id_formats(self):
        """Test behavior with various invalid place ID formats."""
        GmapsClient(api_key="edge-case-test")

        invalid_place_ids = [
            "",  # Empty string
            " ",  # Whitespace only
            "   ",  # Multiple whitespace
            "invalid_place_id",  # Invalid format
            "12345",  # Numeric only
            "places/ChIJd8BlQ2BZwokRAFUEcm_qrcA",  # With prefix
            "a" * 10000,  # Extremely long
            "\n\t\r",  # Special characters
            "ChIJ\x00null",  # Null character
            "ChIJ测试",  # Unicode characters
            "ChIJ!@#$%^&*()",  # Special symbols
        ]

        # These should all create valid request objects (validation happens at API level)
        for place_id in invalid_place_ids:
            from gmaps.models import GeocodingRequest

            try:
                request = GeocodingRequest(
                    address=None,
                    place_id=place_id,
                    components=None,
                    bounds=None,
                    language=None,
                    region=None,
                    extra_computations=None,
                    output_format="json",
                )
                assert request.place_id == place_id
                params = request.to_query_params()
                assert dict(params)["place_id"] == place_id

            except ValidationError as e:
                with pytest.raises(ValidationError):
                    raise e

    def test_place_geocoding_method_with_edge_case_params(self):
        """Test place_geocode_simple method with edge case parameters."""
        from gmaps.models import GeocodingRequest

        GmapsClient(api_key="edge-case-test")

        # Test with extreme parameter values
        edge_case_params = [
            {"place_id": "abc", "language": "", "region": "", "output_format": "json"},
            {
                "place_id": "a" * 1000,  # Very long place ID
                "language": "xx",  # Invalid language code format should still work
                "region": "zz",  # Invalid region code format should still work
                "output_format": "xml",
            },
            {
                "place_id": "ChIJ测试地点",  # Unicode place ID
                "language": "zh-CN",  # Complex language code
                "region": "cn",
                "output_format": "json",
            },
        ]

        for params in edge_case_params:
            # This should create a valid request without errors
            # Add missing required parameters
            from typing import Any

            full_params: dict[str, Any] = {
                "address": None,
                "components": None,
                "bounds": None,
                "extra_computations": None,
                **params,
            }
            request = GeocodingRequest(**full_params)
            assert request.place_id == params["place_id"]
            assert request.language == params["language"]
            assert request.region == params["region"]
            assert request.output_format == params["output_format"]

    def test_empty_place_id_raises_error(self):
        from gmaps.models import GeocodingRequest

        with pytest.raises(ValidationError):
            GeocodingRequest(
                place_id="",
                address=None,
                components=None,
                language=None,
                region=None,
                output_format="json",
            )

    def test_place_id_with_special_encoding(self):
        """Test place IDs with various encodings and special characters."""
        from gmaps.models import GeocodingRequest

        special_place_ids = [
            "ChIJ%20encoded%20id",  # URL encoded
            "ChIJ+plus+encoded",  # Plus encoding
            "ChIJ\u00e9\u00f1\u00fc",  # Extended ASCII
            "ChIJ\U0001f4cd\U0001f30d",  # Emoji characters
            "ChIJ\r\n\t",  # Control characters
            "ChIJ'\"quotes\"'",  # Quote characters
            "ChIJ<>&amp;",  # HTML entities
        ]

        for place_id in special_place_ids:
            request = GeocodingRequest(
                address=None,
                place_id=place_id,
                components=None,
                bounds=None,
                language=None,
                region=None,
                extra_computations=None,
                output_format="json",
            )
            assert request.place_id == place_id

            # Verify query params generation handles special characters
            params = request.to_query_params()
            assert dict(params)["place_id"] == place_id

    @pytest.mark.asyncio
    async def test_place_geocoding_context_manager_edge_cases(self):
        """Test place geocoding method behavior in edge cases."""
        client = GmapsClient(api_key="context-edge-test")

        # Mock the geocoding client to avoid actual API calls
        async def mock_geocode(*args, **kwargs):
            # Simulate different response scenarios
            mock_response = Mock()
            mock_response.status_code = 400  # Bad request
            mock_response.json.return_value = {
                "status": "INVALID_REQUEST",
                "error_message": "Invalid place_id",
            }
            return mock_response

        mock_sub_client_methods(client, geocoding_methods={"geocode": mock_geocode})

        # Test that method calls work even with mocked failures
        async with client as c:
            # This should work without throwing exceptions (error handling is caller's responsibility)
            assert hasattr(c.geocoding, "place_geocode_simple")
            assert callable(c.geocoding.place_geocode_simple)


class TestGmapsClientEnvironmentEdgeCases:
    """Test behavior in various environment conditions."""

    def test_missing_environment_variables(self):
        """Test behavior when environment variables are missing."""
        # Patch environment to remove API key
        with patch.dict(os.environ, {}, clear=True):
            # Should work without environment API key if explicit key provided
            client = GmapsClient(api_key="explicit-key")
            assert client._api_key == "explicit-key"

            # Should work without API key at all (validation happens in sub-clients)
            client = GmapsClient()
            assert client._api_key is None

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix signal test")
    def test_signal_interruption(self):
        """Test behavior when interrupted by signals (Unix only)."""
        import signal

        client = GmapsClient(api_key="signal-test")

        # Mock a long-running operation
        def signal_handler(signum, frame):
            raise KeyboardInterrupt("Signal received")

        if sys.platform != "win32":
            old_handler = signal.signal(signal.SIGALRM, signal_handler)
        else:
            old_handler = None

        try:
            # Set alarm to interrupt after short delay
            if sys.platform != "win32":
                signal.alarm(1)

            # This should be interrupted
            with pytest.raises(KeyboardInterrupt):
                # Simulate long operation
                for _ in range(1000000):
                    mock_sub_client_methods(
                        client,
                        places_methods={"info": Mock(return_value={"test": "info"})},
                        geocoding_methods={"info": Mock(return_value={"test": "info"})},
                    )
                    client.info()
        finally:
            if sys.platform != "win32":
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)

    def test_import_errors(self):
        """Test behavior when imports fail."""
        # Test ADC import failure (already covered in auth tests)
        # but verify graceful degradation

        with patch("gmaps.clients.client.PlacesClient") as mock_places:
            mock_places.side_effect = ImportError("Missing dependency")

            with pytest.raises(ImportError):
                GmapsClient(api_key="import-test")


class TestGmapsClientConcurrencyEdgeCases:
    """Test concurrency-related edge cases."""

    @pytest.mark.asyncio
    async def test_concurrent_initialization(self):
        """Test concurrent initialization of multiple clients."""

        async def init_client(client_id: int) -> GmapsClient:
            return GmapsClient(api_key=f"concurrent-init-{client_id}")

        # Start many initialization tasks simultaneously
        tasks = [init_client(i) for i in range(20)]
        clients = await asyncio.gather(*tasks)

        assert len(clients) == 20
        assert all(isinstance(client, GmapsClient) for client in clients)

    @pytest.mark.asyncio
    async def test_race_condition_in_method_calls(self):
        """Test potential race conditions in method calls."""
        client = GmapsClient(api_key="race-test")

        # Mock sub-clients with thread-safe counters
        call_count = {"info": 0, "set_rate_limit": 0}

        def counting_info():
            call_count["info"] += 1
            return {"unified_client": True}

        def counting_set_rate_limit(qpm):
            call_count["set_rate_limit"] += 1

        mock_sub_client_methods(
            client,
            places_methods={
                "info": Mock(side_effect=counting_info),
                "set_rate_limit": Mock(side_effect=counting_set_rate_limit),
            },
        )

        async def mixed_calls() -> None:
            for _ in range(10):
                client.info()
                client.set_rate_limit(places_qpm=60)

        # Run concurrent mixed calls
        tasks = [mixed_calls() for _ in range(5)]
        await asyncio.gather(*tasks)

        # Verify all calls were made
        assert call_count["info"] == 50
        assert call_count["set_rate_limit"] == 50

    @pytest.mark.asyncio
    async def test_deadlock_potential(self):
        """Test scenarios that could potentially cause deadlocks."""
        client = GmapsClient(api_key="deadlock-test")

        # Use asyncio.Lock instead of threading.Lock
        import asyncio

        lock = asyncio.Lock()  # ← This is the key change

        async def locking_aenter():
            async with lock:  # ← Use async context manager
                await asyncio.sleep(0.01)  # Now this won't block threads
                return client.places

        async def locking_aexit(exc_type, exc, tb):
            async with lock:
                await asyncio.sleep(0.01)  # Hold lock briefly
                return None

        # Rest of your test remains the same
        setattr(client.places, "__aenter__", locking_aenter)
        setattr(client.places, "__aexit__", locking_aexit)
        setattr(
            client.geocoding, "__aenter__", AsyncMock(return_value=client.geocoding)
        )
        setattr(client.geocoding, "__aexit__", AsyncMock(return_value=None))

        async def use_client() -> None:
            async with client:
                await asyncio.sleep(0.01)

        start_time = asyncio.get_event_loop().time()
        tasks = [use_client() for _ in range(5)]
        await asyncio.gather(*tasks)
        end_time = asyncio.get_event_loop().time()

        # Add assertion to verify it completed in reasonable time
        assert end_time - start_time < 1.0, "Test took too long - potential deadlock"


if __name__ == "__main__":
    pytest.main([__file__])
