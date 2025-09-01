"""
Application settings and configuration.
"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Database settings
    database_url: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./log_simulator.db"
    )
    
    # Redis settings
    redis_url: str = os.getenv(
        "REDIS_URL", 
        "redis://localhost:6379"
    )
    
    # Application settings
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    class Config:
        env_file = ".env"


settings = Settings()