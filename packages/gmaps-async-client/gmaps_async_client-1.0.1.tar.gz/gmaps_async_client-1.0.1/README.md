# gmaps-async-client

Async Python client for Google Maps APIs (Places & Geocoding) with httpx and Pydantic.

[![codecov](https://codecov.io/gh/asparagusbeef/gmaps-async-client/branch/main/graph/badge.svg)](https://codecov.io/gh/asparagusbeef/gmaps-async-client)
[![PyPI version](https://badge.fury.io/py/gmaps-async-client.svg)](https://badge.fury.io/py/gmaps-async-client)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

**Problem**: Need async Google Places (New) and Geocoding API access with proper typing, rate limiting, and flexible configuration.
**Solution**: Unified client with Places (nearby/text search, details, autocomplete) and Geocoding APIs, HTTP/2 support, and centralized settings.

## Note

This is a work-in-progress. Response models are not yet implemented, and not all routes are implemented. Feel free to contribute!

## Installation

```bash
# Basic
pip install gmaps-async-client

# With Google ADC auth support
pip install gmaps-async-client[google]
```

## Quick Start

```python
from gmaps import GmapsClient

async def main():
    async with GmapsClient() as client:
        # Places API - search nearby
        response = await client.places.nearby_search_simple(
            latitude=37.7749, longitude=-122.4194, radius=1000
        )

        # Places API - text search
        response = await client.places.text_search_simple(
            query="coffee shops in San Francisco"
        )

        # Geocoding API - address to coords
        response = await client.geocoding.geocode_simple(
            address="1600 Amphitheatre Parkway, Mountain View, CA"
        )

        # Geocoding API - place ID to address
        response = await client.geocoding.place_geocode_simple(
            place_id="ChIJd8BlQ2BZwokRAFUEcm_qrcA"
        )

        # Parse responses
        data = response.json()
        print(data)

import asyncio
asyncio.run(main())
```

## Authentication

Auth priority: API key (param/env) → Google ADC → error

```bash
# Option 1: Environment variable
export GOOGLE_PLACES_API_KEY="your-key"

# Option 2: Google ADC (requires gmaps[google])
gcloud auth application-default login
```

```python
# Explicit API key
client = GmapsClient(api_key="your-key")

# Force ADC mode
client = GmapsClient(auth_mode=AuthMode.ADC)
```


## Configuration

### Basic Configuration

```python
from gmaps import GmapsClient, ClientOptions, RetryConfig
import httpx

options = ClientOptions(
    timeout=httpx.Timeout(30.0),
    retry=RetryConfig(max_attempts=3),
    enable_logging=True
)

client = GmapsClient(
    options=options,
    places_qpm=100,      # Places API rate limit
    geocoding_qpm=50     # Geocoding API rate limit
)
```

### Environment Variables

Centralized configuration via environment variables (prefix: `GMAPS_`):

`GMAPS_GOOGLE_PLACES_API_KEY` - The Google Places API key. Also accepts `GOOGLE_PLACES_API_KEY` as an alias.
`GMAPS_STRICT_PLACE_TYPE_VALIDATION` - Whether to strictly validate place types against the types in [Table A](https://developers.google.com/maps/documentation/places/web-service/place-types#table-a). Possible values: `true` or `false`. Default is `true`.

### Custom Type Registration

Register custom place types, components, or extra computations. Useful if the API changes and the SDK is not updated yet.

```python
from gmaps import register_custom, get_custom, clear_custom_registries

# Register custom place types
register_custom("place_types", "custom_restaurant", "special_shop")

# Register custom geocoding components
register_custom("components", "custom_area", "special_zone")

# Register custom extra computations
register_custom("extra_computations", "CUSTOM_COMPUTATION", "SPECIAL_FEATURE")

# View registered values
print(get_custom("place_types"))  # {'custom_restaurant', 'special_shop'}
print(get_custom("components"))   # {'custom_area', 'special_zone'}

# Clear
clear_custom_registries()
```

## API Methods

### Places API

```python
# Nearby search
response = await client.places.nearby_search_simple(
    latitude=37.7749, longitude=-122.4194, radius=1000,
    included_types=["restaurant"], max_results=10
)

# Text search
response = await client.places.text_search_simple(
    query="pizza restaurants", max_results=10
)

# Place details
response = await client.places.place_details_simple(
    place_id="ChIJN1t_tDeuEmsRUsoyG83frY4",
    session_token="your-session-token"  # Optional for billing optimization
)

# Autocomplete
response = await client.places.autocomplete_simple(
    input_text="coffee shop",
    included_primary_types=["cafe"],
    session_token="your-session-token",  # Optional for billing optimization
    field_mask=["suggestions.placePrediction.text.text"]  # Control returned fields
)
```

### Geocoding API

```python
# Address to coordinates
response = await client.geocoding.geocode_simple(
    address="1600 Amphitheatre Parkway, Mountain View, CA"
)

# Place ID to address (place geocoding)
response = await client.geocoding.place_geocode_simple(
    place_id="ChIJd8BlQ2BZwokRAFUEcm_qrcA",
    language="en",
    region="us"
)
```

### Advanced Usage

```python
from gmaps import (
    GmapsClient, NearbySearchRequest, Circle, LatLng,
    LocationRestriction, GeocodingRequest
)

# Full request objects for complex queries
request = NearbySearchRequest(
    location_restriction=LocationRestriction(
        circle=Circle(
            center=LatLng(latitude=37.7749, longitude=-122.4194),
            radius=1500.0
        )
    ),
    included_types=["restaurant"],
    max_result_count=20
)

response = await client.places.nearby_search(
    request=request,
    field_mask=["places.displayName", "places.rating"]
)
```

## Response Handling

```python
response = await client.places.text_search_simple(query="pizza")
data = response.json()

# Places API responses
for place in data.get("places", []):
    name = place.get("displayName", {}).get("text")
    address = place.get("formattedAddress")
    rating = place.get("rating")

# Geocoding API responses
for result in data.get("results", []):
    coords = result["geometry"]["location"]
    lat, lng = coords["lat"], coords["lng"]
```

**Field Masks**: Control returned data for performance
```python
field_mask = ["places.displayName", "places.location"]
```

## Error Handling

```python
import httpx
from gmaps import GmapsClient

async with GmapsClient() as client:
    try:
        response = await client.places.text_search_simple(query="restaurants")
        data = response.json()
    except httpx.HTTPStatusError as e:
        print(f"HTTP {e.response.status_code}: {e.response.text}")
    except httpx.RequestError as e:
        print(f"Network error: {e}")
```

## Available Models

All models can be imported directly from `gmaps`:

```python
from gmaps import (
    # Clients
    GmapsClient, PlacesClient, GeocodingClient,
    # Configuration
    ClientOptions, RateLimitConfig, AuthMode, RetryConfig,
    # Request models
    NearbySearchRequest, TextSearchRequest, DetailsRequest,
    AutocompleteRequest, GeocodingRequest,
    # Location models
    LatLng, Circle, LocationRestriction, LocationBias, Viewport,
    # Component models
    ComponentFilter, Component,
    # Enums
    RankPreference, PriceLevel, EVConnectorType, ExtraComputations,
    # Custom registration hooks
    register_custom, get_custom, clear_custom_registries, CustomField
)
```



## Requirements

- Python 3.9+
- httpx >= 0.25.0
- pydantic >= 2.0.0
- pydantic-settings >= 2.0.0
- h2 >= 4.3.0 (for HTTP/2)
- google-auth (for ADC)

## Links

[GitHub](https://github.com/asparagusbeef/gmaps-async-client) • [PyPI](https://pypi.org/project/gmaps-async-client/) • [Google Maps API](https://developers.google.com/maps)
