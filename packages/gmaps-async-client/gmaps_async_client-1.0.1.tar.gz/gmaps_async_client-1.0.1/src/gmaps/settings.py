"""
Centralized configuration system for gmaps.
Uses Pydantic BaseSettings for automatic environment variable handling.
"""

from functools import lru_cache
from typing import Optional

from pydantic import AliasChoices, Field, SecretStr
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
    google_places_api_key: Optional[SecretStr] = Field(
        default=None,
        validation_alias=AliasChoices(
            "GMAPS_GOOGLE_PLACES_API_KEY",
            "GOOGLE_PLACES_API_KEY",
        ),
        description="The Google Places API key.",
    )


@lru_cache(maxsize=1)
def get_config() -> Settings:
    return Settings.model_validate({})


def reload_config() -> Settings:
    get_config.cache_clear()
    return get_config()
