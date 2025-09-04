"""Enviroment configuration for the application."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # FASTAPI
    API_TITLE: str = "Youtube Rag"
    API_DESCRIPTION: str = "A simple Youtube RAG application"
    API_VERSION: str = "1.0.0"
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost"]
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"

    # LLM API
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-5-mini-2025-08-07"
    GOOGLE_API_KEY: str = ""
    GOOGLE_MODEL: str = "gemini-1.5-flash"
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-5-haiku-20241022"

    MIGRATIONS_FOLDER_PATH: str = "migrations"


settings = Settings()
