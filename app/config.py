"""Application configuration."""

import os


class Settings:
    """Application settings."""

    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./leads.db")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")


settings = Settings()
