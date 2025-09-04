"""
Application settings and configuration.
"""
import os
from typing import Optional
from pydantic import Field, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    ENVIRONMENT: str
    SECRET_KEY: str
    FERNET_KEY: str
    ORIGINS: Optional[str]
    OTELE_TRACE: bool = False
    LOGGING_LEVEL: str = "DEBUG"

    authjwt_secret_key: str = Field(validation_alias="SECRET_KEY")
    authjwt_token_location: set = {"cookies", "headers"}
    authjwt_cookie_csrf_protect: bool = True
    authjwt_access_token_expires: int
    authjwt_refresh_token_expires: int
    authjwt_denylist_enabled: bool = True
    authjwt_denylist_token_checks: set = {"access", "refresh"}
    authjwt_algorithm: str = "HS256"

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key_env(cls, v):
        # Handle empty secret key for development environments
        if not v or v.strip() == "":
            return "dev-secret-key-not-configured"  # Provide a default for dev
        return v

    @field_validator("FERNET_KEY")
    @classmethod
    def validate_fernet_key(cls, v):
        # Handle empty fernet key for development environments
        if not v or v.strip() == "":
            return "dev-fernet-key-not-configured"  # Provide a default for dev
        return v

    @field_validator("authjwt_secret_key")
    @classmethod
    def validate_secret_key(cls, v):
        # Handle empty secret key for development environments
        if not v or v.strip() == "":
            return "dev-secret-key-not-configured"  # Provide a default for dev
        return v
    
    # Database settings
    APP_DB_URI : str
    DB_SSL_ENABLED: Optional[bool] = False
    
    # Redis settings
    REDIS_URI: str
    
    # Application settings
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    app_title: str = "Log Simulator"
    
    model_config = SettingsConfigDict(
        env_file=".env", extra="allow", env_nested_delimiter="__"
    )
from functools import lru_cache
@lru_cache
def get_settings():
    return Settings()


cfg: Settings = Settings()