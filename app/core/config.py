from typing import List
from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Secret keys and API keys
    JWT_SECRET: str = Field("supersecret", description="JWT secret key")
    JWT_ALGORITHM: str = Field("HS256", description="JWT algorithm for signing tokens")
    JWT_EXPIRATION_MINUTES: int = Field(60, description="JWT token expiration time in minutes")
    HTTP_API_KEY: str = Field("123456", description="HTTP API key for authentication")

    # CORS settings
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl | str] = Field(
        ["http://localhost:8000", "*"], description="List of allowed CORS origins for the backend"
    )

    # Configuration for Pydantic settings
    model_config = SettingsConfigDict(env_prefix="TSKZ_", env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()

if __name__ == "__main__":
    # Debugging: Print the settings to verify they are loaded correctly
    from pprint import pprint

    pprint(settings.model_dump(), width=120)  # Debug statement to verify settings loading
