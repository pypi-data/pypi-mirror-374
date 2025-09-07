"""
Tests for Geocoding API models and request validation.

This module contains tests for the GeocodingRequest model validation,
particularly the new place_id functionality and parameter validation.
"""

from typing import Any

import pytest
from pydantic import ValidationError
from typing_extensions import Literal

from gmaps.models import Component, ComponentFilter, GeocodingRequest, LatLng, Viewport


def create_geocoding_request(**kwargs: Any) -> GeocodingRequest:
    """Helper function to create GeocodingRequest with all optional parameters."""
    defaults: dict[str, Any] = {
        "address": None,
        "place_id": None,
        "components": None,
        "bounds": None,
        "language": None,
        "region": None,
        "extra_computations": None,
        "output_format": "json",
    }
    defaults.update(kwargs)
    return GeocodingRequest(**defaults)


class TestGeocodingRequest:
    """Test cases for GeocodingRequest model validation."""

    def test_geocoding_request_with_address(self):
        """Test creating GeocodingRequest with address parameter."""
        request = create_geocoding_request(
            address="1600 Amphitheatre Parkway, Mountain View, CA",
            language="en",
            region="us",
        )

        assert request.address == "1600 Amphitheatre Parkway, Mountain View, CA"
        assert request.place_id is None
        assert request.components is None
        assert request.language == "en"
        assert request.region == "us"
        assert request.output_format == "json"  # default

    def test_geocoding_request_with_place_id(self):
        """Test creating GeocodingRequest with place_id parameter."""
        place_id = "ChIJd8BlQ2BZwokRAFUEcm_qrcA"
        request = create_geocoding_request(
            place_id=place_id, language="en", region="us"
        )

        assert request.place_id == place_id
        assert request.address is None
        assert request.components is None
        assert request.language == "en"
        assert request.region == "us"

    def test_geocoding_request_with_components(self):
        """Test creating GeocodingRequest with components parameter."""
        components = [
            ComponentFilter(component=Component.LOCALITY, value="Mountain View"),
            ComponentFilter(component=Component.COUNTRY, value="US"),
        ]

        request = create_geocoding_request(components=components, language="en")

        assert request.components == components
        assert request.address is None
        assert request.place_id is None

    def test_geocoding_request_validation_requires_one_param(self):
        """Test that GeocodingRequest requires at least one of address, place_id, or components."""
        # Should fail with no parameters
        with pytest.raises(
            ValidationError,
            match="You must specify either 'address', 'place_id', or 'components'",
        ):
            create_geocoding_request()

        # Should fail with only optional parameters
        with pytest.raises(
            ValidationError,
            match="You must specify either 'address', 'place_id', or 'components'",
        ):
            create_geocoding_request(language="en", region="us")

    def test_geocoding_request_allows_multiple_params(self):
        """Test that GeocodingRequest allows multiple required parameters."""
        # Should work with address and components together
        components = [ComponentFilter(component=Component.COUNTRY, value="US")]
        request = GeocodingRequest(address="Mountain View", components=components)
        assert request.address == "Mountain View"
        assert request.components == components

        # Should work with place_id and other params
        request = GeocodingRequest(
            place_id="ChIJd8BlQ2BZwokRAFUEcm_qrcA", language="en"
        )
        assert request.place_id == "ChIJd8BlQ2BZwokRAFUEcm_qrcA"
        assert request.language == "en"

    def test_geocoding_request_place_id_types(self):
        """Test different place_id value types and formats."""
        # Standard place ID
        request = GeocodingRequest(place_id="ChIJd8BlQ2BZwokRAFUEcm_qrcA")
        assert request.place_id == "ChIJd8BlQ2BZwokRAFUEcm_qrcA"

        # Place ID with special characters
        request = GeocodingRequest(place_id="ChIJN1t_tDeuEmsRUsoyG83frY4")
        assert request.place_id == "ChIJN1t_tDeuEmsRUsoyG83frY4"

        with pytest.raises(ValidationError):
            GeocodingRequest(place_id="")

    def test_geocoding_request_output_format_validation(self):
        """Test output format validation."""
        # Valid formats
        formats: list[Literal["json", "xml"]] = ["json", "xml"]
        for format_type in formats:
            request = GeocodingRequest(address="test", output_format=format_type)
            assert request.output_format == format_type

        # Invalid format should raise validation error
        with pytest.raises(ValidationError):
            GeocodingRequest(address="test", output_format="yaml")  # type: ignore

    def test_geocoding_request_bounds_validation(self):
        """Test bounds parameter validation."""
        # Valid bounds
        bounds = Viewport(
            low=LatLng(latitude=37.0, longitude=-122.5),
            high=LatLng(latitude=37.5, longitude=-122.0),
        )

        request = GeocodingRequest(address="test", bounds=bounds)
        assert request.bounds == bounds

        # Invalid bounds (low > high latitude) should raise error
        with pytest.raises(ValidationError, match="Viewport is empty"):
            invalid_bounds = Viewport(
                low=LatLng(
                    latitude=37.5, longitude=-122.5
                ),  # Higher latitude than 'high'
                high=LatLng(latitude=37.0, longitude=-122.0),
            )
            GeocodingRequest(address="test", bounds=invalid_bounds)

    def test_geocoding_request_to_query_params(self):
        """Test conversion to query parameters."""
        # Test with place_id
        request = GeocodingRequest(
            place_id="ChIJd8BlQ2BZwokRAFUEcm_qrcA", language="en", region="us"
        )

        params = request.to_query_params()
        params_dict = dict(params)

        assert params_dict["place_id"] == "ChIJd8BlQ2BZwokRAFUEcm_qrcA"
        assert params_dict["language"] == "en"
        assert params_dict["region"] == "us"
        assert "address" not in params_dict

        # Test with address
        request = GeocodingRequest(
            address="1600 Amphitheatre Parkway, Mountain View, CA", language="fr"
        )

        params = request.to_query_params()
        params_dict = dict(params)

        assert params_dict["address"] == "1600 Amphitheatre Parkway, Mountain View, CA"
        assert params_dict["language"] == "fr"
        assert "place_id" not in params_dict

        # Test with components
        components = [
            ComponentFilter(component=Component.LOCALITY, value="Mountain View"),
            ComponentFilter(component=Component.COUNTRY, value="US"),
        ]
        request = GeocodingRequest(components=components)

        params = request.to_query_params()
        params_dict = dict(params)

        assert (
            "locality:Mountain View|country:US" in params_dict["components"]
        ), f"Unexpected components: {params_dict['components']}"
        assert "place_id" not in params_dict
        assert "address" not in params_dict

    def test_geocoding_request_to_query_params_with_bounds(self):
        """Test query params generation with bounds parameter."""
        bounds = Viewport(
            low=LatLng(latitude=37.0, longitude=-122.5),
            high=LatLng(latitude=37.5, longitude=-122.0),
        )

        request = GeocodingRequest(place_id="test_place_id", bounds=bounds)

        params = request.to_query_params()
        params_dict = dict(params)

        assert params_dict["place_id"] == "test_place_id"
        assert params_dict["bounds"] == "37.0,-122.5|37.5,-122.0"

    def test_geocoding_request_all_parameters_together(self):
        """Test GeocodingRequest with all possible parameters."""
        bounds = Viewport(
            low=LatLng(latitude=37.0, longitude=-122.5),
            high=LatLng(latitude=37.5, longitude=-122.0),
        )

        request = GeocodingRequest(
            place_id="ChIJd8BlQ2BZwokRAFUEcm_qrcA",
            bounds=bounds,
            language="es",
            region="mx",
            extra_computations=["ADDRESS_DESCRIPTORS"],
            output_format="xml",
        )

        assert request.place_id == "ChIJd8BlQ2BZwokRAFUEcm_qrcA"
        assert request.bounds == bounds
        assert request.language == "es"
        assert request.region == "mx"
        assert request.extra_computations == ["ADDRESS_DESCRIPTORS"]
        assert request.output_format == "xml"

        # Test query params generation
        params = request.to_query_params()
        params_dict = dict(params)

        assert params_dict["place_id"] == "ChIJd8BlQ2BZwokRAFUEcm_qrcA"
        assert params_dict["bounds"] == "37.0,-122.5|37.5,-122.0"
        assert params_dict["language"] == "es"
        assert params_dict["region"] == "mx"
        assert "ADDRESS_DESCRIPTORS" in dict(params).get("extra_computations", "")

    def test_geocoding_request_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Very long place ID
        long_place_id = "a" * 1000
        request = GeocodingRequest(place_id=long_place_id)
        assert request.place_id == long_place_id

        # Place ID with special characters
        special_place_id = "ChIJ!@#$%^&*()_+-={}[]|\\:;\"'<>?,./~`"
        request = GeocodingRequest(place_id=special_place_id)
        assert request.place_id == special_place_id

        # Unicode place ID
        unicode_place_id = "ChIJ测试地点ID"
        request = GeocodingRequest(place_id=unicode_place_id)
        assert request.place_id == unicode_place_id

    def test_geocoding_request_immutability(self):
        """Test that request objects maintain consistent state."""
        request = GeocodingRequest(
            place_id="ChIJd8BlQ2BZwokRAFUEcm_qrcA", language="en"
        )

        # Generate params multiple times - should be consistent
        params1 = request.to_query_params()
        params2 = request.to_query_params()

        assert dict(params1) == dict(params2)

        # Original request should be unchanged
        assert request.place_id == "ChIJd8BlQ2BZwokRAFUEcm_qrcA"
        assert request.language == "en"


if __name__ == "__main__":
    pytest.main([__file__])
