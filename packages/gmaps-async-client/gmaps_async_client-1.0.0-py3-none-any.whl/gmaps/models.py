from __future__ import annotations

import warnings
from enum import Enum
from typing import Any, Literal, Optional, Union

from httpx import QueryParams
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)
from typing_extensions import Self

from .constants import PLACE_TYPES
from .settings import get_config


def _to_camel(s: str) -> str:
    parts = s.split("_")
    return parts[0] + "".join(p.capitalize() or "_" for p in parts[1:])


def _components_allowlist() -> set[str]:
    raw = get_config().components_allowlist
    return {s.strip() for s in raw}


def _extra_computations_allowlist() -> set[str]:
    raw = get_config().extra_computations_allowlist
    return {s.strip() for s in raw}


def _validate_place_type(v: str, err_msg: str = "") -> str:
    if not err_msg:
        err_msg = f"Invalid place type: {v}"
    for _, types in PLACE_TYPES.items():
        if v in types:
            return v
    if v in get_config().place_types_allowlist:
        return v
    if get_config().strict_place_type_validation:
        raise ValueError(err_msg)
    else:
        warnings.warn(err_msg, stacklevel=2)
    return v


class CamelModel(BaseModel):
    """
    Base model that:
      - Accepts snake_case or camelCase on input (populate_by_name=True + alias_generator)
      - Emits camelCase on output (via .to_request_dict() helper or model_dump(..., by_alias=True))
      - Serializes Enums/values as JSON primitives (mode="json")
    """

    model_config = ConfigDict(
        alias_generator=_to_camel,
        populate_by_name=True,
    )

    def to_request_dict(
        self,
        *,
        exclude_none: bool = True,
        extra_dump_kwargs: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Standardized dump for request bodies:
          - camelCase keys (by_alias=True)
          - enum values as strings/numbers (mode="json")
          - exclude None fields by default
        """
        kwargs: dict[str, Any] = {
            "by_alias": True,
            "mode": "json",
            "exclude_none": exclude_none,
        }
        if extra_dump_kwargs:
            kwargs.update(extra_dump_kwargs)
        return self.model_dump(**kwargs)


class RankPreference(str, Enum):
    """Ranking preference for search results."""

    POPULARITY = "POPULARITY"
    DISTANCE = "DISTANCE"
    RELEVANCE = "RELEVANCE"


class PriceLevel(str, Enum):
    """Price level options for filtering search results."""

    INEXPENSIVE = "PRICE_LEVEL_INEXPENSIVE"
    MODERATE = "PRICE_LEVEL_MODERATE"
    EXPENSIVE = "PRICE_LEVEL_EXPENSIVE"
    VERY_EXPENSIVE = "PRICE_LEVEL_VERY_EXPENSIVE"


class EVConnectorType(str, Enum):
    """EV charging connector types."""

    UNSPECIFIED = "EV_CONNECTOR_TYPE_UNSPECIFIED"
    OTHER = "EV_CONNECTOR_TYPE_OTHER"
    J1772 = "EV_CONNECTOR_TYPE_J1772"
    TYPE_2 = "EV_CONNECTOR_TYPE_TYPE_2"
    CCS_COMBO_1 = "EV_CONNECTOR_TYPE_CCS_COMBO_1"
    CCS_COMBO_2 = "EV_CONNECTOR_TYPE_CCS_COMBO_2"
    TESLA = "EV_CONNECTOR_TYPE_TESLA"
    GBT = "EV_CONNECTOR_TYPE_GBT"
    UNSPECIFIED_WALL_OUTLET = "EV_CONNECTOR_TYPE_UNSPECIFIED_WALL_OUTLET"


class LatLng(BaseModel):
    """Geographic coordinates (latitude and longitude)."""

    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude in degrees")
    longitude: float = Field(
        ..., ge=-180.0, le=180.0, description="Longitude in degrees"
    )


class Circle(BaseModel):
    """A circle defined by center point and radius."""

    center: LatLng = Field(..., description="Center point of the circle")
    radius: float = Field(..., gt=0.0, le=50000.0, description="Radius in meters")


class LocationRestriction(BaseModel):
    """Location restriction for search queries."""

    circle: Circle = Field(..., description="Circular area to search within")


class Viewport(BaseModel):
    """A latitude-longitude viewport, represented as two diagonally opposite points."""

    low: LatLng = Field(..., description="The southwest corner of the viewport.")
    high: LatLng = Field(..., description="The northeast corner of the viewport.")

    @model_validator(mode="after")
    def validate_viewport(self) -> Self:
        """Ensures the viewport is valid and not empty."""
        if self.low and self.high and self.low.latitude > self.high.latitude:
            raise ValueError(
                "Viewport is empty: low.latitude cannot be greater than high.latitude"
            )
        return self


class LocationBias(BaseModel):
    """Specifies an area to search, serving as a bias for results."""

    rectangle: Optional[Viewport] = None
    circle: Optional[Circle] = None

    @model_validator(mode="after")
    def validate_oneof(self) -> Self:
        """Ensures that exactly one of rectangle or circle is set."""
        if self.rectangle is None and self.circle is None:
            raise ValueError(
                "Either 'rectangle' or 'circle' must be set for LocationBias"
            )
        if self.rectangle is not None and self.circle is not None:
            raise ValueError(
                "'rectangle' and 'circle' cannot both be set for LocationBias"
            )
        return self


class TextSearchLocationRestriction(BaseModel):
    """Specifies an area to search, where results outside are not returned."""

    rectangle: Viewport = Field(
        ..., description="The rectangular viewport to restrict results to."
    )


class EVOptions(BaseModel):
    """Parameters for identifying available electric vehicle (EV) charging options."""

    minimum_charging_rate_kw: Optional[float] = Field(
        None,
        ge=0.0,
        description="Minimum EV charging rate in kilowatts (kW). Filters out places with lower rates.",
    )
    connector_types: Optional[list[EVConnectorType]] = Field(
        None,
        max_length=50,  # Assumption, not specified
        description="Filters by available EV charging connector types.",
    )


class NearbySearchRequest(CamelModel):
    """Request model for Google Places API Nearby Search (New)."""

    # Required parameters
    location_restriction: LocationRestriction = Field(
        ..., description="The region to search specified as a circle"
    )

    # Type filtering parameters
    included_types: Optional[list[str]] = None
    excluded_types: Optional[list[str]] = None
    included_primary_types: Optional[list[str]] = None
    excluded_primary_types: Optional[list[str]] = None

    # Search configuration parameters
    max_result_count: Optional[int] = 20
    rank_preference: Optional[RankPreference] = RankPreference.POPULARITY

    # Localization parameters
    language_code: Optional[str] = None
    region_code: Optional[str] = None

    @field_validator("rank_preference", mode="after")
    @classmethod
    def validate_rank_preference(
        cls, v: Optional[RankPreference]
    ) -> Optional[RankPreference]:
        if v is not None:
            if v == RankPreference.RELEVANCE:
                raise ValueError(
                    "Rank preference cannot be RELEVANCE for nearby search"
                )
            return v
        return None

    @field_validator(
        "included_types",
        "excluded_types",
        "included_primary_types",
        "excluded_primary_types",
        mode="after",
    )
    @classmethod
    def validate_type_lists(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        if v is not None:
            if len(v) > 50:
                raise ValueError("Type lists cannot contain more than 50 items")
            for place_type in v:
                if not place_type or not place_type.strip():
                    raise ValueError("Place types must be non-empty strings")
                _validate_place_type(place_type)
        return v

    @field_validator("max_result_count", mode="after")
    @classmethod
    def validate_max_result_count(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and (v < 1 or v > 20):
            raise ValueError("max_result_count must be between 1 and 20")
        return v

    @field_validator("language_code", mode="after")
    @classmethod
    def validate_language_code(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip().lower()
            if len(v) < 2:
                raise ValueError("Language code must be at least 2 characters")
        return v

    @field_validator("region_code", mode="after")
    @classmethod
    def validate_region_code(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip().lower()
            if len(v) != 2:
                raise ValueError("Region code must be exactly 2 characters")
        return v

    @model_validator(mode="after")
    def validate_conflicting_types(self) -> Self:
        if self.included_types and self.excluded_types:
            conflicts = set(self.included_types).intersection(self.excluded_types)
            if conflicts:
                raise ValueError(
                    f"Types cannot be both included and excluded: {conflicts}"
                )

        if self.included_primary_types and self.excluded_primary_types:
            conflicts = set(self.included_primary_types).intersection(
                self.excluded_primary_types
            )
            if conflicts:
                raise ValueError(
                    f"Primary types cannot be both included and excluded: {conflicts}"
                )
        return self


class TextSearchRequest(CamelModel):
    """Request model for Google Places API Text Search (New)."""

    # Required Parameters
    text_query: str = Field(
        ...,
        description='The text string to search for, e.g., "restaurant" or "123 Main Street".',
    )

    # Optional Parameters
    included_type: Optional[str] = Field(
        None,
        description="Biases results to places of the specified type. Only one type may be specified.",
    )
    strict_type_filtering: Optional[bool] = Field(
        False,
        description="When true, only returns places that match the included_type. Default is false.",
    )
    include_pure_service_area_businesses: Optional[bool] = Field(
        False,
        description="Includes businesses that deliver to customers but lack a physical location.",
    )
    language_code: Optional[str] = Field(
        None, description="The language code for returning results, e.g., 'en' or 'fr'."
    )
    region_code: Optional[str] = Field(
        None,
        description="The region code (CLDR) to format the response and bias results, e.g., 'us' or 'fr'.",
    )
    rank_preference: Optional[RankPreference] = Field(
        None,
        description="Specifies how results are ranked. RELEVANCE is default for categorical queries.",
    )
    min_rating: Optional[float] = Field(
        None,
        ge=0.0,
        le=5.0,
        description="Restricts results to those with an average user rating >= this value (0.0-5.0).",
    )
    open_now: Optional[bool] = Field(
        None,
        description="If true, returns only places open for business at the time of the query.",
    )
    price_levels: Optional[list[PriceLevel]] = Field(
        None,
        description="Restricts the search to places marked with certain price levels.",
    )
    page_size: Optional[int] = Field(
        20, ge=1, le=20, description="The number of results to display per page (1-20)."
    )
    page_token: Optional[str] = Field(
        None,
        description="The nextPageToken from a previous response to fetch the next page of results.",
    )
    location_bias: Optional[LocationBias] = Field(
        None,
        description="Specifies an area to search, biasing results to this location.",
    )
    location_restriction: Optional[TextSearchLocationRestriction] = Field(
        None,
        description="Specifies an area to search, returning only results within this area.",
    )
    ev_options: Optional[EVOptions] = Field(
        None,
        description="Parameters for filtering Electric Vehicle (EV) charging options.",
    )

    # Deprecated Parameters
    max_result_count: Optional[int] = Field(
        None,
        ge=1,
        le=20,
        deprecated=True,
        description="Deprecated in favor of pageSize. Specifies the number of results per page (1-20).",
    )

    @field_validator("included_type", mode="after")
    @classmethod
    def validate_included_type(cls, v: Optional[str]) -> Optional[str]:
        """Validates that the included_type is a valid place type."""
        if v is not None:
            return _validate_place_type(v, "Invalid place type for included_type")
        return v

    @field_validator("language_code", mode="after")
    @classmethod
    def validate_language_code(cls, v: Optional[str]) -> Optional[str]:
        """Strips and validates the language_code."""
        if v is not None:
            v = v.strip().lower()
            if len(v) < 2:
                raise ValueError("Language code must be at least 2 characters")
        return v

    @field_validator("region_code", mode="after")
    @classmethod
    def validate_region_code(cls, v: Optional[str]) -> Optional[str]:
        """Strips and validates the region_code."""
        if v is not None:
            v = v.strip().lower()
            if len(v) != 2:
                raise ValueError("Region code must be exactly 2 characters")
        return v

    @field_validator("price_levels", mode="after")
    @classmethod
    def validate_price_levels(
        cls, v: Optional[list[PriceLevel]]
    ) -> Optional[list[PriceLevel]]:
        """Ensures that PRICE_LEVEL_FREE is not included in the request."""
        # The PriceLevel enum does not contain a FREE member, so this check is implicitly handled.
        # Adding an explicit check would be redundant unless the enum changes.
        return v

    @model_validator(mode="after")
    def check_location_fields(self) -> Self:
        """Validates that location_bias and location_restriction are mutually exclusive."""
        if self.location_bias and self.location_restriction:
            raise ValueError(
                "location_bias and location_restriction cannot both be set"
            )
        return self

    @model_validator(mode="after")
    def handle_deprecated_max_result_count(self) -> Self:
        """Handles the deprecated max_result_count field, prioritizing page_size."""
        if self.max_result_count is not None and self.page_size != 20:
            # If both are set, the API will use page_size.
            # We can enforce this or raise a warning. Here we simply let page_size take precedence.
            pass
        elif self.max_result_count is not None:
            self.page_size = self.max_result_count
        return self


class DetailsRequest(CamelModel):
    """Request model for Google Places API Place Details (New)."""

    # Required Parameters
    place_id: str = Field(
        ...,
        description="A textual identifier that uniquely identifies a place.",
    )

    # Optional Parameters
    language_code: Optional[str] = Field(
        None, description="The language in which to return results."
    )
    region_code: Optional[str] = Field(
        None,
        description="The regional code to format the response, as a two-character CLDR code.",
    )
    session_token: Optional[str] = Field(
        None,
        description="A user-generated string to track Autocomplete sessions for billing.",
    )

    @field_validator("place_id", mode="after")
    @classmethod
    def validate_place_id(cls, v: str) -> str:
        """Validates that the place_id is a non-empty string."""
        if not v or not v.strip():
            raise ValueError("place_id must be a non-empty string")
        if v.startswith("places/"):
            v = v[len("places/") :]
        return v

    @field_validator("language_code", mode="after")
    @classmethod
    def validate_language_code(cls, v: Optional[str]) -> Optional[str]:
        """Strips and validates the language_code."""
        return TextSearchRequest.validate_language_code(v)

    @field_validator("region_code", mode="after")
    @classmethod
    def validate_region_code(cls, v: Optional[str]) -> Optional[str]:
        """Strips and validates the region_code."""
        return TextSearchRequest.validate_region_code(v)


class AutocompleteCircle(Circle):
    """A circle for Autocomplete location restriction, radius must be > 0."""

    radius: float = Field(
        ...,
        gt=0.0,
        le=50000.0,
        description="Radius in meters, must be greater than 0.0",
    )


class AutocompleteLocationRestriction(BaseModel):
    """Specifies an area to search for Autocomplete. Results outside are not returned."""

    rectangle: Optional[Viewport] = None
    circle: Optional[AutocompleteCircle] = None

    @model_validator(mode="after")
    def validate_oneof(self) -> Self:
        """Ensures that exactly one of rectangle or circle is set."""
        if self.rectangle is None and self.circle is None:
            raise ValueError(
                "Either 'rectangle' or 'circle' must be set for AutocompleteLocationRestriction"
            )
        if self.rectangle is not None and self.circle is not None:
            raise ValueError(
                "'rectangle' and 'circle' cannot both be set for AutocompleteLocationRestriction"
            )
        return self


class AutocompleteRequest(CamelModel):
    """Request model for Google Places API Autocomplete (New)."""

    # Required Parameters
    input: str = Field(..., description="The text string to search on.")

    # Optional Parameters
    included_primary_types: Optional[list[str]] = Field(
        None, max_length=5, description="Restricts results to up to five primary types."
    )
    include_pure_service_area_businesses: Optional[bool] = Field(
        False,
        description="Includes businesses that deliver to customers but lack a physical location.",
    )
    include_query_predictions: Optional[bool] = Field(
        False,
        description="If true, the response includes both place and query predictions.",
    )
    included_region_codes: Optional[list[str]] = Field(
        None,
        max_length=15,
        description="Include results only from a list of up to 15 ccTLD country codes.",
    )
    input_offset: Optional[int] = Field(
        None,
        ge=0,
        description="The zero-based Unicode character offset of the cursor in the input string.",
    )
    language_code: Optional[str] = Field(
        None, description="The preferred language for results (IETF BCP-47 code)."
    )
    origin: Optional[LatLng] = Field(
        None,
        description="The origin point from which to calculate straight-line distance to the destination.",
    )
    region_code: Optional[str] = Field(
        None,
        description="The region code (ccTLD) to format the response and bias results.",
    )
    session_token: Optional[str] = Field(
        None,
        description="A user-generated string to track Autocomplete sessions for billing.",
    )
    location_bias: Optional[LocationBias] = Field(
        None,
        description="Specifies an area to search, biasing results to this location.",
    )
    location_restriction: Optional[AutocompleteLocationRestriction] = Field(
        None,
        description="Specifies an area to search, returning only results within this area.",
    )

    @field_validator("input", mode="after")
    @classmethod
    def validate_input(cls, v: str) -> str:
        """Validates that the input is a non-empty string."""
        if not v or not v.strip():
            raise ValueError("input must be a non-empty string")
        return v

    @field_validator("language_code", mode="after")
    @classmethod
    def validate_language_code(cls, v: Optional[str]) -> Optional[str]:
        """Strips and validates the language_code."""
        return TextSearchRequest.validate_language_code(v)

    @field_validator("region_code", mode="after")
    @classmethod
    def validate_region_code(cls, v: Optional[str]) -> Optional[str]:
        """Strips and validates the region_code."""
        return TextSearchRequest.validate_region_code(v)

    @field_validator("included_region_codes", mode="after")
    @classmethod
    def validate_included_region_codes(
        cls, v: Optional[list[str]]
    ) -> Optional[list[str]]:
        """Validates that each region code is a 2-character string."""
        if v:
            for code in v:
                if len(code) != 2:
                    raise ValueError(
                        f"Invalid region code '{code}': must be 2 characters."
                    )
        return v

    @field_validator("included_primary_types", mode="after")
    @classmethod
    def validate_included_primary_types(
        cls, v: Optional[list[str]]
    ) -> Optional[list[str]]:
        """Validates the special conditions for included_primary_types."""
        if v:
            has_regions = "(regions)" in v
            has_cities = "(cities)" in v
            if (has_regions or has_cities) and len(v) > 1:
                raise ValueError(
                    "If '(regions)' or '(cities)' is specified, no other types are allowed."
                )
        return v

    @model_validator(mode="after")
    def check_location_fields(self) -> Self:
        """Validates that location_bias and location_restriction are mutually exclusive."""
        if self.location_bias and self.location_restriction:
            raise ValueError(
                "location_bias and location_restriction cannot both be set"
            )
        return self


class Component(str, Enum):
    """Component types for Geocoding component filtering."""

    POSTAL_CODE = "postal_code"
    COUNTRY = "country"
    ROUTE = "route"
    LOCALITY = "locality"
    ADMINISTRATIVE_AREA = "administrative_area"


ComponentStr = Union[str, Component]


class ComponentFilter(BaseModel):
    """A single component filter for a Geocoding request."""

    component: ComponentStr
    value: str

    def to_str(self) -> str:
        """Formats the component filter for the URL."""
        return f"{self.component}:{self.value}"

    @field_validator("component", mode="after")
    @classmethod
    def validate_component(cls, v: ComponentStr) -> str:
        """Validates that the component is a valid component."""
        if isinstance(v, Component):
            return v.value
        v = str(v).strip()
        if v in _components_allowlist():
            return v
        else:
            raise ValueError(
                f"Invalid component '{v}'. Add it to EXTRA_COMPONENTS environment variable to allow it."
            )


class ExtraComputations(str, Enum):
    """Extra computations that can be requested."""

    ADDRESS_DESCRIPTORS = "ADDRESS_DESCRIPTORS"
    BUILDING_AND_ENTRANCES = "BUILDING_AND_ENTRANCES"


ExtraComputationsStr = Union[str, ExtraComputations]


class GeocodingRequest(BaseModel):
    """
    Pydantic model for validating and building Geocoding API query parameters.
    This model is not for a JSON request body, but for constructing a URL.
    """

    address: Optional[str] = Field(
        None, description="The street address or plus code that you want to geocode."
    )
    components: Optional[list[ComponentFilter]] = Field(
        None, description="A list of component filters to restrict results."
    )
    bounds: Optional[Viewport] = Field(
        None, description="The bounding box of the viewport to bias results."
    )
    language: Optional[str] = Field(
        None, description="The language in which to return results."
    )
    region: Optional[str] = Field(
        None, description="The region code (ccTLD) to bias results."
    )
    extra_computations: Optional[list[ExtraComputationsStr]] = Field(
        None, description="Specifies additional features in the response."
    )
    output_format: Literal["json", "xml"] = Field(
        "json", description="The format of the response."
    )

    @model_validator(mode="before")
    @classmethod
    def check_address_or_components(cls, data: Any) -> Any:
        """Ensures that either 'address' or 'components' is provided."""
        if isinstance(data, dict):
            if not data.get("address") and not data.get("components"):
                raise ValueError("You must specify either 'address' or 'components'.")
        return data

    @field_validator("extra_computations", mode="after")
    @classmethod
    def validate_extra_computations(
        cls, v: Optional[list[ExtraComputationsStr]]
    ) -> Optional[list[ExtraComputationsStr]]:
        """Validates that the extra_computations are a valid extra_computations."""
        if v:
            for ec in v:
                if (
                    not isinstance(ec, ExtraComputations)
                    and ec not in _extra_computations_allowlist()
                ):
                    raise ValueError(
                        f"Invalid extra computation '{ec}'. Add it to EXTRA_EXTRA_COMPUTATIONS environment variable to allow it."
                    )
        return v

    def to_query_params(self) -> QueryParams:
        """
        Serializes the model fields into a dictionary suitable for URL query parameters.
        """
        params = QueryParams()
        if self.address:
            params = params.add("address", self.address)

        if self.components:
            params = params.add(
                "components", "|".join(c.to_str() for c in self.components)
            )

        if self.bounds:
            low = self.bounds.low
            high = self.bounds.high
            params = params.add(
                "bounds",
                (f"{low.latitude},{low.longitude}|{high.latitude},{high.longitude}"),
            )

        if self.language:
            params = params.add("language", self.language)

        if self.region:
            params = params.add("region", self.region)

        if self.extra_computations:
            for ec in self.extra_computations:
                if isinstance(ec, ExtraComputations):
                    ec = ec.value
                params = params.add("extra_computations", ec)

        return params
