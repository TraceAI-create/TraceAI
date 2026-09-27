from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str

    # Supabase Storage configuration (optional)
    supabase_url: str | None = None
    supabase_key: str | None = None
    supabase_storage_bucket: str = "traceai-evidence"

    # Local storage fallback directory
    local_storage_dir: str = "data/evidence"

    # API configuration
    api_v1_prefix: str = "/api/v1"
    project_name: str = "TraceAI"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()