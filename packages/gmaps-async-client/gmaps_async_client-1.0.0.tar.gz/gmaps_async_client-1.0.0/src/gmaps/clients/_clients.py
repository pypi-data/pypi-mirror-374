"""
Google Places and Geocoding API client implementation.

This module provides the main PlacesClient and GeocodingClient classes for interacting with
the Google Places API (New) and Geocoding API, including nearby search, text search,
geocoding, and reverse geocoding functionality.
"""

from __future__ import annotations

from typing import Any, Literal, Optional, Union

import httpx

from ..config import ClientOptions
from ..models import (
    AutocompleteRequest,
    Circle,
    ComponentFilter,
    DetailsRequest,
    GeocodingRequest,
    LatLng,
    LocationBias,
    LocationRestriction,
    NearbySearchRequest,
    RankPreference,
    TextSearchRequest,
    Viewport,
)
from ._auth import AuthMode
from ._base import GeocodingBaseClient, PlacesBaseClient


class PlacesClient(PlacesBaseClient):
    """
    Async client for Google Places API (New).

    This client provides access to Places API endpoints including nearby search,
    text search, place details, and autocomplete functionality.

    Available methods:
    - nearby_search() / nearby_search_simple(): Search for places near a location
    - text_search() / text_search_simple(): Search for places using text queries
    - place_details() / place_details_simple(): Get detailed info about a place
    - autocomplete() / autocomplete_simple(): Get place suggestions as user types

    Example:
        ```python
        from gmaps.places import PlacesClient, NearbySearchRequest, Circle, LatLng, LocationRestriction

        async with PlacesClient() as client:
            # Nearby search
            request = NearbySearchRequest(
                location_restriction=LocationRestriction(
                    circle=Circle(
                        center=LatLng(latitude=37.7749, longitude=-122.4194),
                        radius=1000.0
                    )
                ),
                included_types=["restaurant"],
                max_result_count=10
            )

            response = await client.nearby_search(
                request=request,
                field_mask=["places.displayName", "places.formattedAddress"]
            )

            # Or use simplified methods
            response = await client.text_search_simple(
                query="pizza restaurants",
                max_results=10
            )
        ```
    """

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        auth_mode: Optional[AuthMode] = None,
        options: Optional[ClientOptions] = None,
        qpm: Optional[int] = None,
    ) -> None:
        """
        Initialize Places API client.

        Args:
            api_key: Google Maps API key. If not provided, will use GOOGLE_PLACES_API_KEY env var
            auth_mode: Authentication mode (API_KEY or ADC). Auto-detected if not specified
            options: Client configuration options
            qpm: Queries per minute rate limit. Defaults to 60 if not specified
        """
        super().__init__(api_key=api_key, auth_mode=auth_mode, options=options, qpm=qpm)

    async def __aenter__(self) -> PlacesClient:
        """Async context manager entry."""
        await super().__aenter__()
        return self

    async def nearby_search(
        self,
        *,
        request: NearbySearchRequest,
        field_mask: Union[str, list[str]],
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Perform a Nearby Search (New) request.

        Searches for places within a specified area. This is the new version of the
        Nearby Search API that uses POST requests and provides more precise control
        over results.

        Args:
            request: The nearby search request parameters
            field_mask: Fields to return in the response. Can be a string like
                       "places.displayName,places.formattedAddress" or a list of strings.
                       Use "*" to get all fields (not recommended for production).
            **kwargs: Additional keyword arguments passed to the HTTP request

        Returns:
            httpx.Response: Raw HTTP response from the API

        Raises:
            ValueError: If field_mask is empty or request validation fails
            GMapsError: If the API returns an error response

        Example:
            ```python
            from gmaps.places import NearbySearchRequest, Circle, LatLng, LocationRestriction

            request = NearbySearchRequest(
                location_restriction=LocationRestriction(
                    circle=Circle(
                        center=LatLng(latitude=37.7749, longitude=-122.4194),
                        radius=1000.0
                    )
                ),
                included_types=["restaurant", "cafe"],
                max_result_count=20,
                rank_preference="DISTANCE"
            )

            response = await client.nearby_search(
                request=request,
                field_mask=[
                    "places.displayName",
                    "places.formattedAddress",
                    "places.rating",
                    "places.priceLevel"
                ]
            )
            ```
        """
        # Prepare field mask header
        if not field_mask:
            raise ValueError("field_mask is required and cannot be empty")

        if isinstance(field_mask, list):
            field_mask_str = ",".join(field_mask)
        else:
            field_mask_str = str(field_mask)

        # Remove any spaces from field mask (not allowed per API docs)
        field_mask_str = field_mask_str.replace(" ", "")

        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "X-Goog-FieldMask": field_mask_str,
        }

        # Add any additional headers from kwargs
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        # Prepare request body
        request_body = request.to_request_dict()

        # Make the API request
        response = await self._request(
            method="POST",
            url="/places:searchNearby",
            json=request_body,
            headers=headers,
            **kwargs,
        )

        return response

    async def nearby_search_simple(
        self,
        *,
        latitude: float,
        longitude: float,
        radius: float,
        included_types: Optional[list[str]] = None,
        max_results: int = 20,
        rank_by_distance: bool = False,
        field_mask: Optional[Union[str, list[str]]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Simplified nearby search method with common parameters.

        This is a convenience method that creates a NearbySearchRequest internally
        for common use cases.

        Args:
            latitude: Center latitude for search
            longitude: Center longitude for search
            radius: Search radius in meters (max 50000)
            included_types: List of place types to include (e.g., ["restaurant", "cafe"])
            max_results: Maximum number of results (1-20)
            rank_by_distance: If True, rank by distance. If False, rank by popularity
            field_mask: Fields to return. If None, returns basic fields
            **kwargs: Additional arguments passed to nearby_search()

        Returns:
            httpx.Response: Raw HTTP response from the API

        Example:
            ```python
            response = await client.nearby_search_simple(
                latitude=37.7749,
                longitude=-122.4194,
                radius=1000,
                included_types=["restaurant"],
                max_results=10,
                rank_by_distance=True
            )
            ```
        """

        # Create request object
        request = NearbySearchRequest(
            location_restriction=LocationRestriction(
                circle=Circle(
                    center=LatLng(latitude=latitude, longitude=longitude), radius=radius
                )
            ),
            included_types=included_types,
            excluded_types=None,
            included_primary_types=None,
            excluded_primary_types=None,
            max_result_count=max_results,
            rank_preference=(
                RankPreference.DISTANCE
                if rank_by_distance
                else RankPreference.POPULARITY
            ),
            language_code=None,
            region_code=None,
        )

        # Default field mask if not provided
        if field_mask is None:
            field_mask = [
                "places.displayName",
                "places.formattedAddress",
                "places.location",
                "places.types",
            ]

        return await self.nearby_search(
            request=request, field_mask=field_mask, **kwargs
        )

    async def text_search(
        self,
        *,
        request: TextSearchRequest,
        field_mask: Union[str, list[str]],
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Perform a Text Search (New) request.

        Searches for places using a text query string. This method supports
        location biasing/restriction, type filtering, and various other parameters.

        Args:
            request: The text search request parameters
            field_mask: Fields to return in the response. Can be a string like
                       "places.displayName,places.formattedAddress" or a list of strings.
                       Use "*" to get all fields (not recommended for production).
            **kwargs: Additional keyword arguments passed to the HTTP request

        Returns:
            httpx.Response: Raw HTTP response from the API

        Raises:
            ValueError: If field_mask is empty or request validation fails
            GMapsError: If the API returns an error response

        Example:
            ```python
            from gmaps.places import TextSearchRequest

            request = TextSearchRequest(
                text_query="restaurants near Times Square",
                included_type="restaurant",
                language_code="en",
                region_code="us",
                page_size=10
            )

            response = await client.text_search(
                request=request,
                field_mask=[
                    "places.displayName",
                    "places.formattedAddress",
                    "places.rating",
                    "places.location"
                ]
            )
            ```
        """
        # Prepare field mask header
        if not field_mask:
            raise ValueError("field_mask is required and cannot be empty")

        if isinstance(field_mask, list):
            field_mask_str = ",".join(field_mask)
        else:
            field_mask_str = str(field_mask)

        # Remove any spaces from field mask (not allowed per API docs)
        field_mask_str = field_mask_str.replace(" ", "")

        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "X-Goog-FieldMask": field_mask_str,
        }

        # Add any additional headers from kwargs
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        # Prepare request body
        request_body = request.to_request_dict()

        # Make the API request
        response = await self._request(
            method="POST",
            url="/places:searchText",
            json=request_body,
            headers=headers,
            **kwargs,
        )

        return response

    async def text_search_simple(
        self,
        *,
        query: str,
        included_type: Optional[str] = None,
        language_code: Optional[str] = None,
        region_code: Optional[str] = None,
        max_results: int = 20,
        location_bias: Optional[LocationBias] = None,
        field_mask: Optional[Union[str, list[str]]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Simplified text search method with common parameters.

        This is a convenience method that creates a TextSearchRequest internally
        for common use cases.

        Args:
            query: The text string to search for (e.g., "pizza near me", "123 Main St")
            included_type: Filter to places of this type (e.g., "restaurant", "gas_station")
            language_code: Language for results (e.g., "en", "es")
            region_code: Region code for formatting (e.g., "us", "fr")
            max_results: Maximum number of results to return (1-20)
            location_bias: Bias results to a specific location area
            field_mask: Fields to return. If None, returns basic fields
            **kwargs: Additional arguments passed to text_search()

        Returns:
            httpx.Response: Raw HTTP response from the API

        Example:
            ```python
            response = await client.text_search_simple(
                query="coffee shops in Manhattan",
                included_type="cafe",
                language_code="en",
                region_code="us",
                max_results=10
            )
            ```
        """
        # Create request object
        request = TextSearchRequest(
            text_query=query,
            included_type=included_type,
            strict_type_filtering=None,
            include_pure_service_area_businesses=None,
            language_code=language_code,
            region_code=region_code,
            rank_preference=None,
            min_rating=None,
            open_now=None,
            price_levels=None,
            page_size=max_results,
            page_token=None,
            location_bias=location_bias,
            location_restriction=None,
            ev_options=None,
            max_result_count=None,
        )

        # Default field mask if not provided
        if field_mask is None:
            field_mask = [
                "places.displayName",
                "places.formattedAddress",
                "places.location",
                "places.rating",
                "places.types",
            ]

        return await self.text_search(request=request, field_mask=field_mask, **kwargs)

    async def place_details(
        self,
        *,
        request: DetailsRequest,
        field_mask: Union[str, list[str]],
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Get detailed information about a specific place.

        Retrieves comprehensive details about a place using its place_id.
        This includes information like contact details, opening hours, reviews,
        photos, and more depending on the field mask provided.

        Args:
            request: The place details request parameters
            field_mask: Fields to return in the response. Can be a string like
                       "displayName,formattedAddress" or a list of strings.
                       Use "*" to get all fields (not recommended for production).
            **kwargs: Additional keyword arguments passed to the HTTP request

        Returns:
            httpx.Response: Raw HTTP response from the API

        Raises:
            ValueError: If field_mask is empty or request validation fails
            GMapsError: If the API returns an error response

        Example:
            ```python
            from gmaps.places import DetailsRequest

            request = DetailsRequest(
                place_id="ChIJN1t_tDeuEmsRUsoyG83frY4",
                language_code="en",
                region_code="us"
            )

            response = await client.place_details(
                request=request,
                field_mask=[
                    "displayName",
                    "formattedAddress",
                    "internationalPhoneNumber",
                    "websiteUri",
                    "regularOpeningHours",
                    "rating",
                    "userRatingCount",
                    "reviews"
                ]
            )
            ```
        """
        # Prepare field mask header
        if not field_mask:
            raise ValueError("field_mask is required and cannot be empty")

        if isinstance(field_mask, list):
            field_mask_str = ",".join(field_mask)
        else:
            field_mask_str = str(field_mask)

        # Remove any spaces from field mask (not allowed per API docs)
        field_mask_str = field_mask_str.replace(" ", "")

        # Prepare headers
        headers = {
            "X-Goog-FieldMask": field_mask_str,
        }

        # Add any additional headers from kwargs
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        # For place details, we need to extract the place_id and make a GET request
        # The URL format is /places/{place_id}
        place_id = request.place_id

        # Prepare query parameters from the request
        params = httpx.QueryParams()
        if request.language_code:
            params = params.add("languageCode", request.language_code)
        if request.region_code:
            params = params.add("regionCode", request.region_code)
        if request.session_token:
            params = params.add("sessionToken", request.session_token)

        # Make the API request
        response = await self._request(
            method="GET",
            url=f"/places/{place_id}",
            params=params,
            headers=headers,
            **kwargs,
        )

        return response

    async def place_details_simple(
        self,
        *,
        place_id: str,
        language_code: Optional[str] = None,
        region_code: Optional[str] = None,
        field_mask: Optional[Union[str, list[str]]] = None,
        session_token: Optional[str] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Simplified place details method with common parameters.

        This is a convenience method that creates a DetailsRequest internally
        for common use cases.

        Args:
            place_id: The place ID to get details for
            language_code: Language for results (e.g., "en", "es")
            region_code: Region code for formatting (e.g., "us", "fr")
            field_mask: Fields to return. If None, returns basic fields
            session_token: Session token to pass as additional context
            **kwargs: Additional arguments passed to place_details()

        Returns:
            httpx.Response: Raw HTTP response from the API

        Example:
            ```python
            response = await client.place_details_simple(
                place_id="ChIJN1t_tDeuEmsRUsoyG83frY4",
                language_code="en",
                region_code="us",
                session_token="1234567890"
            )
            ```
        """
        # Create request object
        request = DetailsRequest(
            place_id=place_id,
            language_code=language_code,
            region_code=region_code,
            session_token=session_token,
        )

        # Default field mask if not provided
        if field_mask is None:
            field_mask = [
                "displayName",
                "formattedAddress",
                "internationalPhoneNumber",
                "websiteUri",
                "location",
                "rating",
                "userRatingCount",
                "regularOpeningHours",
            ]

        return await self.place_details(
            request=request, field_mask=field_mask, **kwargs
        )

    async def autocomplete(
        self,
        *,
        request: AutocompleteRequest,
        field_mask: Optional[Union[str, list[str]]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Get place autocomplete predictions.

        Returns place predictions for a user's search input. This is typically
        used to provide search suggestions as the user types.

        Args:
            request: The autocomplete request parameters
            field_mask: Fields to return. If None, returns basic fields
            **kwargs: Additional keyword arguments passed to the HTTP request

        Returns:
            httpx.Response: Raw HTTP response from the API

        Raises:
            ValueError: If request validation fails
            GMapsError: If the API returns an error response

        Example:
            ```python
            from gmaps.places import AutocompleteRequest, LocationBias, Circle, LatLng

            request = AutocompleteRequest(
                input="pizza restaurant",
                included_primary_types=["restaurant"],
                language_code="en",
                region_code="us",
                location_bias=LocationBias(
                    circle=Circle(
                        center=LatLng(latitude=37.7749, longitude=-122.4194),
                        radius=5000.0
                    )
                )
            )

            response = await client.autocomplete(request=request)
            ```
        """
        headers = {
            "Content-Type": "application/json",
        }
        if field_mask:  # Optional in autocomplete request
            if isinstance(field_mask, list):
                field_mask_str = ",".join(field_mask)
            else:
                field_mask_str = str(field_mask)

            field_mask_str = field_mask_str.replace(" ", "")
            headers["X-Goog-FieldMask"] = field_mask_str

        # Add any additional headers from kwargs
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        # Prepare request body
        request_body = request.to_request_dict()

        # Make the API request
        response = await self._request(
            method="POST",
            url="/places:autocomplete",
            json=request_body,
            headers=headers,
            **kwargs,
        )

        return response

    async def autocomplete_simple(
        self,
        *,
        input_text: str,
        language_code: Optional[str] = None,
        region_code: Optional[str] = None,
        location_bias: Optional[LocationBias] = None,
        included_primary_types: Optional[list[str]] = None,
        field_mask: Optional[Union[str, list[str]]] = None,
        session_token: Optional[str] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Simplified autocomplete method with common parameters.

        This is a convenience method that creates an AutocompleteRequest internally
        for common use cases.

        Args:
            input_text: The text string to get predictions for
            language_code: Language for results (e.g., "en", "es")
            region_code: Region code for formatting (e.g., "us", "fr")
            location_bias: Bias results to a specific location area
            included_primary_types: Restrict results to these place types
            field_mask: Fields to return. If None, returns basic fields
            session_token: Session token to pass as additional context
            **kwargs: Additional arguments passed to autocomplete()

        Returns:
            httpx.Response: Raw HTTP response from the API

        Example:
            ```python
            response = await client.autocomplete_simple(
                input_text="coffee shop",
                language_code="en",
                region_code="us",
                included_primary_types=["cafe", "restaurant"],
                session_token="1234567890"
            )
            ```
        """
        # Create request object
        request = AutocompleteRequest(
            input=input_text,
            included_primary_types=included_primary_types,
            include_pure_service_area_businesses=None,
            include_query_predictions=None,
            included_region_codes=None,
            input_offset=None,
            language_code=language_code,
            origin=None,
            region_code=region_code,
            session_token=session_token,
            location_bias=location_bias,
            location_restriction=None,
        )

        # Default field mask if not provided
        if field_mask is None:
            field_mask = [
                "suggestions.placePrediction.text.text",
                "suggestions.queryPrediction.text.text",
            ]

        return await self.autocomplete(request=request, field_mask=field_mask, **kwargs)


class GeocodingClient(GeocodingBaseClient):
    """
    Async client for Google Geocoding API.

    This client provides access to the Geocoding API for converting addresses to
    geographic coordinates (geocoding) and vice versa (reverse geocoding).

    Available methods:
    - geocode(): Convert addresses to coordinates using full request object
    - geocode_simple(): Simplified geocoding with common parameters

    Example:
        ```python
        from gmaps import GeocodingClient, GeocodingRequest

        async with GeocodingClient() as client:
            # Full geocoding request
            request = GeocodingRequest(
                address="1600 Amphitheatre Parkway, Mountain View, CA",
                language="en",
                region="us"
            )

            response = await client.geocode(request=request)

            # Or use simplified method
            response = await client.geocode_simple(
                address="1600 Amphitheatre Parkway, Mountain View, CA"
            )
        ```
    """

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        auth_mode: Optional[AuthMode] = None,
        options: Optional[ClientOptions] = None,
        qpm: Optional[int] = None,
    ) -> None:
        """
        Initialize Geocoding API client.

        Args:
            api_key: Google Maps API key. If not provided, will use GOOGLE_PLACES_API_KEY env var
            auth_mode: Authentication mode (API_KEY or ADC). Auto-detected if not specified
            options: Client configuration options
            qpm: Queries per minute rate limit. Defaults to 60 if not specified
        """
        super().__init__(api_key=api_key, auth_mode=auth_mode, options=options, qpm=qpm)

    async def __aenter__(self) -> GeocodingClient:
        """Async context manager entry."""
        await super().__aenter__()
        return self

    async def geocode(
        self,
        *,
        request: GeocodingRequest,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Perform a Geocoding API request.

        Converts addresses (like "1600 Amphitheatre Parkway, Mountain View, CA")
        to geographic coordinates (like latitude 37.423021 and longitude -122.083739).

        Args:
            request: The geocoding request parameters
            **kwargs: Additional keyword arguments passed to the HTTP request

        Returns:
            httpx.Response: Raw HTTP response from the API

        Raises:
            ValueError: If request validation fails
            GMapsError: If the API returns an error response

        Example:
            ```python
            from gmaps import GeocodingRequest, ComponentFilter, Component

            request = GeocodingRequest(
                address="1600 Amphitheatre Parkway, Mountain View, CA",
                language="en",
                region="us",
                components=[
                    ComponentFilter(component=Component.COUNTRY, value="US")
                ]
            )

            response = await client.geocode(request=request)
            ```
        """
        # Convert request to query parameters
        params = request.to_query_params()

        # Prepare the URL based on output format
        url_path = f"/{request.output_format}"

        # Make the API request
        # httpx automatically handles list values in params as repeated parameters
        response = await self._request(
            method="GET",
            url=url_path,
            params=params,
            **kwargs,
        )

        return response

    async def geocode_simple(
        self,
        *,
        address: Optional[str] = None,
        components: Optional[list[ComponentFilter]] = None,
        language: Optional[str] = None,
        region: Optional[str] = None,
        bounds: Optional[Viewport] = None,
        output_format: Literal["json", "xml"] = "json",
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Simplified geocoding method with common parameters.

        This is a convenience method that creates a GeocodingRequest internally
        for common use cases.

        Args:
            address: The street address to geocode (e.g., "1600 Amphitheatre Parkway, Mountain View, CA")
            components: List of component filters to restrict results
            language: Language for results (e.g., "en", "es")
            region: Region code for bias (e.g., "us", "fr")
            bounds: Viewport to bias geocode results more prominently
            output_format: Response format ("json" or "xml")
            **kwargs: Additional arguments passed to geocode()

        Returns:
            httpx.Response: Raw HTTP response from the API

        Raises:
            ValueError: If neither address nor components is provided

        Example:
            ```python
            # Geocode a simple address
            response = await client.geocode_simple(
                address="1600 Amphitheatre Parkway, Mountain View, CA",
                language="en",
                region="us"
            )

            # Geocode with component filtering
            response = await client.geocode_simple(
                components=[
                    ComponentFilter(component=Component.LOCALITY, value="Mountain View"),
                    ComponentFilter(component=Component.COUNTRY, value="US")
                ]
            )
            ```
        """
        # Create request object
        request = GeocodingRequest(
            address=address,
            components=components,
            bounds=bounds,
            language=language,
            region=region,
            extra_computations=None,
            output_format=output_format,
        )

        return await self.geocode(request=request, **kwargs)
