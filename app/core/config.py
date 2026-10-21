
from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Agentic AI Customer Support"
    app_version: str = "0.1.0"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"

    # LLM configuration
    openai_api_key: SecretStr | None = None
    openai_model: str = "gpt-4.1-mini"
    
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    qdrant_collection: str = "support_knowledge"
    chunk_size: int = 1000
    chunk_overlap: int = 150
    max_upload_size_mb: int = 10

    # Vector database configuration
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: SecretStr | None = None

    # Database configuration
    database_url: SecretStr | None = None
    redis_url: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
