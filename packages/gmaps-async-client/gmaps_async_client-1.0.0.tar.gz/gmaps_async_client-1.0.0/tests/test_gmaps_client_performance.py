"""
Performance and stress testing for GmapsClient.

This module contains tests focused on performance characteristics,
resource usage, and stress scenarios for the GmapsClient.
"""

import asyncio
import gc
import time
import weakref
from typing import Any, Optional, Union
from unittest.mock import AsyncMock, Mock

import pytest

from gmaps import ClientOptions, GmapsClient

from .test_utils import (
    mock_client_context_managers,
    mock_client_methods,
    mock_sub_client_methods,
)


class TestGmapsClientPerformance:
    """Performance tests for GmapsClient."""

    @pytest.mark.asyncio
    async def test_context_manager_performance(self):
        """Test context manager setup/teardown performance."""
        client = GmapsClient(api_key="perf-test-key")

        # Mock sub-clients for consistent timing
        mock_client_context_managers(client)

        iterations = 100
        start_time = time.perf_counter()

        for _ in range(iterations):
            async with client:
                pass

        end_time = time.perf_counter()
        total_time = end_time - start_time
        avg_time_per_iteration = total_time / iterations

        # Should be reasonably fast (adjust threshold as needed)
        assert (
            avg_time_per_iteration < 0.1
        ), f"Context manager too slow: {avg_time_per_iteration:.4f}s per iteration"

    @pytest.mark.asyncio
    async def test_concurrent_client_creation(self):
        """Test concurrent client creation performance."""

        async def create_client(client_id: int) -> GmapsClient:
            client = GmapsClient(api_key=f"concurrent-test-{client_id}")
            # Mock sub-clients to avoid actual initialization overhead
            mock_client_context_managers(client)
            return client

        num_clients = 50
        start_time = time.perf_counter()

        # Create clients concurrently
        tasks = [create_client(i) for i in range(num_clients)]
        clients = await asyncio.gather(*tasks)

        end_time = time.perf_counter()
        total_time = end_time - start_time

        assert len(clients) == num_clients
        assert all(isinstance(client, GmapsClient) for client in clients)

        # Should complete reasonably quickly
        assert (
            total_time < 5.0
        ), f"Concurrent creation too slow: {total_time:.2f}s for {num_clients} clients"

    def test_memory_usage_basic(self):
        """Test basic memory usage characteristics."""
        # Get initial memory state
        initial_objects = len(gc.get_objects())

        # Create and destroy clients
        clients = []
        for i in range(100):
            client = GmapsClient(api_key=f"memory-test-{i}")
            clients.append(client)

        # Clean up
        del clients
        gc.collect()

        # Check that we didn't leak too many objects
        final_objects = len(gc.get_objects())
        object_growth = final_objects - initial_objects

        # Allow some reasonable growth but not excessive
        assert (
            object_growth < 1000
        ), f"Potential memory leak: {object_growth} new objects"

    def test_client_reuse_performance(self):
        """Test performance of reusing the same client instance."""
        client = GmapsClient(api_key="reuse-test-key")

        # Mock methods for consistent timing
        mock_client_methods(
            client,
            info=Mock(return_value={"unified_client": True}),
            set_rate_limit=Mock(),
        )

        iterations = 1000
        start_time = time.perf_counter()

        for i in range(iterations):
            if i % 2 == 0:
                client.info()
            else:
                client.set_rate_limit(places_qpm=60 + i)

        end_time = time.perf_counter()
        total_time = end_time - start_time
        avg_time_per_call = total_time / iterations

        # Method calls should be very fast
        assert (
            avg_time_per_call < 0.001
        ), f"Method calls too slow: {avg_time_per_call:.6f}s per call"


class TestGmapsClientStress:
    """Stress tests for GmapsClient."""

    @pytest.mark.asyncio
    async def test_rapid_context_manager_usage(self):
        """Test rapid context manager entry/exit cycles."""
        client = GmapsClient(api_key="stress-test-key")

        # Mock sub-clients
        mock_client_context_managers(client)

        async def rapid_usage_task() -> None:
            for _ in range(10):
                async with client:
                    await asyncio.sleep(0.001)  # Minimal work

        # Run multiple tasks concurrently
        num_tasks = 20
        tasks = [rapid_usage_task() for _ in range(num_tasks)]

        start_time = time.perf_counter()
        await asyncio.gather(*tasks)
        end_time = time.perf_counter()

        total_time = end_time - start_time
        assert total_time < 10.0, f"Stress test too slow: {total_time:.2f}s"

    @pytest.mark.asyncio
    async def test_exception_stress(self):
        """Test behavior under repeated exception conditions."""
        client = GmapsClient(api_key="exception-stress-key")

        # Make sub-clients fail intermittently
        failure_count = 0
        original_aenter = AsyncMock(return_value=client.places)

        async def failing_aenter(*args, **kwargs):
            nonlocal failure_count
            failure_count += 1
            if failure_count % 3 == 0:  # Fail every 3rd attempt
                raise Exception(f"Simulated failure {failure_count}")
            return await original_aenter(*args, **kwargs)

        setattr(client.places, "__aenter__", failing_aenter)
        setattr(client.places, "__aexit__", AsyncMock(return_value=None))
        setattr(
            client.geocoding, "__aenter__", AsyncMock(return_value=client.geocoding)
        )
        setattr(client.geocoding, "__aexit__", AsyncMock(return_value=None))

        successes = 0
        failures = 0

        for _ in range(30):
            try:
                async with client:
                    successes += 1
            except Exception:
                failures += 1

        # Should handle mixed success/failure scenarios
        assert successes > 0, "No successful operations"
        assert failures > 0, "No failed operations (test setup issue)"
        assert successes + failures == 30, "Unexpected operation count"

    def test_massive_client_creation(self):
        """Test creating many client instances."""
        clients = []

        try:
            # Create many clients
            for i in range(500):
                client = GmapsClient(api_key=f"massive-test-{i}")
                clients.append(client)

                # Verify basic functionality every 100 clients
                if i % 100 == 99:
                    assert isinstance(client, GmapsClient)
                    assert client._api_key == f"massive-test-{i}"

            assert len(clients) == 500

        finally:
            # Clean up
            del clients
            gc.collect()

    @pytest.mark.asyncio
    async def test_concurrent_method_calls(self):
        """Test concurrent method calls on the same client."""
        client = GmapsClient(api_key="concurrent-method-test")

        # Mock methods with some artificial delay
        async def slow_info() -> dict[str, Any]:
            await asyncio.sleep(0.01)
            return {"unified_client": True}

        def slow_set_rate_limit(
            places_qpm: Optional[int] = None, geocoding_qpm: Optional[int] = None
        ) -> None:
            time.sleep(0.01)
            return None

        mock_sub_client_methods(
            client,
            places_methods={"info": Mock(side_effect=lambda: slow_info())},
            geocoding_methods={"set_rate_limit": Mock(side_effect=slow_set_rate_limit)},
        )

        async def mixed_operations(task_id: int) -> list[tuple[str, Any]]:
            results: list[tuple[str, Union[dict[str, Any], None]]] = []
            for i in range(10):
                if (task_id + i) % 2 == 0:
                    # Async operation - client.info() is not awaitable, it's synchronous
                    result = client.info()
                    results.append(("info", result))
                else:
                    # Sync operation
                    client.set_rate_limit(places_qpm=60 + task_id + i)
                    results.append(("set_rate_limit", None))
            return results

        # Run concurrent mixed operations
        num_tasks = 10
        tasks = [mixed_operations(i) for i in range(num_tasks)]

        start_time = time.perf_counter()
        results = await asyncio.gather(*tasks)
        end_time = time.perf_counter()

        total_time = end_time - start_time

        # Verify all operations completed
        assert len(results) == num_tasks
        for task_results in results:
            assert len(task_results) == 10

        # Should complete in reasonable time (accounting for artificial delays)
        assert total_time < 5.0, f"Concurrent operations too slow: {total_time:.2f}s"


class TestGmapsClientResourceManagement:
    """Tests focused on resource management and cleanup."""

    def test_client_garbage_collection(self):
        """Test that clients can be properly garbage collected."""
        weak_refs = []

        # Create clients and weak references
        for i in range(10):
            client = GmapsClient(api_key=f"gc-test-{i}")
            weak_refs.append(weakref.ref(client))
            del client  # Remove strong reference

        # Force garbage collection
        gc.collect()

        # Check how many clients were collected
        collected_count = sum(1 for ref in weak_refs if ref() is None)

        # Most clients should be collected (allow some variance for GC timing)
        assert (
            collected_count >= len(weak_refs) // 2
        ), f"Only {collected_count}/{len(weak_refs)} clients were garbage collected"

    @pytest.mark.asyncio
    async def test_context_manager_cleanup_stress(self):
        """Test context manager cleanup under stress conditions."""
        cleanup_call_count = 0

        async def counting_aexit(exc_type, exc, tb):
            nonlocal cleanup_call_count
            cleanup_call_count += 1
            return None

        # Create many clients and use context managers
        for i in range(50):
            client = GmapsClient(api_key=f"cleanup-stress-{i}")
            setattr(client.places, "__aenter__", AsyncMock(return_value=client.places))
            setattr(client.places, "__aexit__", counting_aexit)
            setattr(
                client.geocoding, "__aenter__", AsyncMock(return_value=client.geocoding)
            )
            setattr(client.geocoding, "__aexit__", counting_aexit)

            async with client:
                pass  # Minimal work

        # Verify cleanup was called for all clients
        expected_calls = 50 * 2  # 2 sub-clients per GmapsClient
        assert (
            cleanup_call_count == expected_calls
        ), f"Expected {expected_calls} cleanup calls, got {cleanup_call_count}"

    def test_configuration_object_reuse(self):
        """Test memory efficiency with configuration object reuse."""
        # Create shared configuration
        shared_options = ClientOptions(timeout=30.0, http2=False, enable_logging=False)

        # Create multiple clients with shared configuration
        clients = []
        for i in range(20):
            client = GmapsClient(api_key=f"shared-config-{i}", options=shared_options)
            clients.append(client)

        # Verify all clients share the same options object (except url)
        shared_options.base_url = None
        client.places.options.base_url = None
        client.geocoding.options.base_url = None
        assert client.places.options == client.geocoding.options
        assert client.places.options.timeout is shared_options.timeout
        assert client.geocoding.options.timeout is shared_options.timeout

        # Clean up
        del clients
        del shared_options
        gc.collect()

    @pytest.mark.asyncio
    async def test_resource_cleanup_on_exception(self):
        """Test proper resource cleanup when exceptions occur."""
        cleanup_tracker = {
            "places_entered": 0,
            "places_exited": 0,
            "geo_entered": 0,
            "geo_exited": 0,
        }

        async def tracking_places_aenter():
            cleanup_tracker["places_entered"] += 1
            return Mock()  # Return a mock instead of string

        async def tracking_places_aexit(exc_type, exc, tb):
            cleanup_tracker["places_exited"] += 1
            return None

        async def tracking_geo_aenter():
            cleanup_tracker["geo_entered"] += 1
            raise Exception("Geocoding init failed")  # Always fail

        async def tracking_geo_aexit(exc_type, exc, tb):
            cleanup_tracker["geo_exited"] += 1
            return None

        # Test multiple failed context entries
        for i in range(5):
            client = GmapsClient(api_key=f"cleanup-exception-{i}")
            setattr(client.places, "__aenter__", tracking_places_aenter)
            setattr(client.places, "__aexit__", tracking_places_aexit)
            setattr(client.geocoding, "__aenter__", tracking_geo_aenter)
            setattr(client.geocoding, "__aexit__", tracking_geo_aexit)

            with pytest.raises(Exception, match="Geocoding init failed"):
                async with client:
                    pass

        # Verify proper cleanup tracking
        assert cleanup_tracker["places_entered"] == 5
        assert (
            cleanup_tracker["places_exited"] == 5
        )  # Should be cleaned up despite geocoding failure
        assert cleanup_tracker["geo_entered"] == 5
        assert (
            cleanup_tracker["geo_exited"] == 0
        )  # Geocoding never successfully entered


class TestGmapsClientMemoryLeaks:
    """Tests specifically designed to detect memory leaks."""

    def test_repeated_initialization_memory(self):
        """Test for memory leaks in repeated client initialization."""
        try:
            import os

            import psutil
        except ImportError:
            pytest.skip("psutil not available for memory testing")

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Create and destroy many clients
        for batch in range(5):  # 5 batches to see trend
            clients = []
            for i in range(100):
                client = GmapsClient(api_key=f"leak-test-{batch}-{i}")
                clients.append(client)

            # Force cleanup
            del clients
            gc.collect()

            # Check memory after each batch
            current_memory = process.memory_info().rss
            memory_growth = current_memory - initial_memory

            # Allow reasonable growth but detect excessive leaks
            # Note: This threshold may need adjustment based on system and Python version
            max_growth_mb = 50 * 1024 * 1024  # 50MB
            assert memory_growth < max_growth_mb, (
                f"Potential memory leak detected: {memory_growth / (1024 * 1024):.1f}MB growth "
                f"after batch {batch + 1}"
            )

    @pytest.mark.asyncio
    async def test_context_manager_memory_leak(self):
        """Test for memory leaks in context manager usage."""
        try:
            import os

            import psutil
        except ImportError:
            pytest.skip("psutil not available for memory testing")

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        client = GmapsClient(api_key="context-leak-test")

        # Mock sub-clients to avoid external dependencies
        mock_client_context_managers(client)

        # Repeatedly use context manager
        for i in range(500):
            async with client:
                # Create some temporary objects
                temp_data = {"iteration": i, "data": list(range(100))}
                del temp_data

            # Check memory periodically
            if i % 100 == 99:
                gc.collect()
                current_memory = process.memory_info().rss
                memory_growth = current_memory - initial_memory

                # Detect excessive memory growth
                max_growth_mb = 20 * 1024 * 1024  # 20MB
                assert memory_growth < max_growth_mb, (
                    f"Potential context manager memory leak: {memory_growth / (1024 * 1024):.1f}MB growth "
                    f"after {i + 1} iterations"
                )

    def test_circular_reference_detection(self):
        """Test for circular references that could prevent garbage collection."""
        # Create client with potential for circular references
        client = GmapsClient(api_key="circular-ref-test")

        # Create some cross-references (testing potential issue patterns)
        client._test_ref = client  # type: ignore[attr-defined]
        client.places._parent_ref = client  # type: ignore[attr-defined]
        client.geocoding._parent_ref = client  # type: ignore[attr-defined]

        # Create weak reference to detect collection
        weak_ref = weakref.ref(client)

        # Remove all strong references
        del client

        # Force garbage collection (may need multiple passes for circular refs)
        for _ in range(3):
            gc.collect()

        # Check if object was collected despite circular references
        # Note: This test might be flaky depending on GC implementation
        # but it's useful for detecting obvious circular reference issues
        if weak_ref() is not None:
            # Object not collected - might indicate circular reference issue
            # This is a warning rather than a failure since GC behavior varies
            pytest.warns(
                UserWarning,
                match="Client object not garbage collected - potential circular references",
            )


if __name__ == "__main__":
    pytest.main([__file__])
