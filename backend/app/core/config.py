"""Application settings and configuration management.

Reads configuration values from environment variables or a .env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """TraceAI application settings."""

    # Database connection string
    database_url: str

    # Supabase cloud storage settings (optional)
    supabase_url: str | None = None
    supabase_key: str | None = None
    supabase_storage_bucket: str = "traceai-evidence"

    # Local folder used if cloud storage is not configured
    local_storage_dir: str = "data/evidence"

    # API configuration
    api_v1_prefix: str = "/api/v1"
    project_name: str = "TraceAI"

    # Settings loader configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Global settings instance
settings = Settings()
