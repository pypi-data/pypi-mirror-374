"""
Centralized configuration system for gmaps.
Uses Pydantic BaseSettings for automatic environment variable handling.
"""

import json
from functools import lru_cache
from typing import Optional, Union, cast

from pydantic import AliasChoices, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings with automatic environment variable loading.

    All settings are automatically loaded from environment variables.
    Uses Pydantic BaseSettings for automatic validation and type conversion.
    """

    model_config = SettingsConfigDict(
        env_prefix="GMAPS_",
    )
    strict_place_type_validation: bool = Field(
        default=True, description="Whether to strictly validate place types."
    )
    place_types_allowlist: tuple[str, ...] = Field(
        default=(),
        description="Extra place types to include in the validation. Useful if API changes and SDK is not updated.",
    )
    google_places_api_key: Optional[SecretStr] = Field(
        default=None,
        validation_alias=AliasChoices(
            "GMAPS_GOOGLE_PLACES_API_KEY",
            "GOOGLE_PLACES_API_KEY",
        ),
        description="The Google Places API key.",
    )
    google_adc_scopes: tuple[str, ...] = Field(
        default=("https://www.googleapis.com/auth/cloud-platform",),
        description="The Google ADC scopes.",
    )
    components_allowlist: tuple[str, ...] = Field(
        default=(),
        description="Allow extra components for validation of Component enum. Useful if API changes and SDK is not updated.",
    )
    extra_computations_allowlist: tuple[str, ...] = Field(
        default=(),
        description="Allow extra extra_computations for validation of ExtraComputations enum. Useful if API changes and SDK is not updated.",
    )

    @field_validator(
        "place_types_allowlist",
        "components_allowlist",
        "google_adc_scopes",
        "extra_computations_allowlist",
        mode="before",
    )
    @classmethod
    def parse_seq_from_env(cls, v: Union[str, list[str]]) -> list[str]:
        if isinstance(v, str):
            s = v.strip()
            if s.startswith("["):
                return cast(list[str], json.loads(s))
            return [x.strip() for x in s.split(",") if x.strip()]
        return v


@lru_cache(maxsize=1)
def get_config() -> Settings:
    return Settings.model_validate({})


def reload_config() -> Settings:
    get_config.cache_clear()
    return get_config()
