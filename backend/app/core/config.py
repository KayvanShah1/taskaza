import os
from typing import List

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Path(BaseSettings):
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    LOGS_DIR: str = os.path.join(BASE_DIR, "logs")
    STATIC_DIR: str = os.path.join(BASE_DIR, "static")
    TEMPLATES_DIR: str = os.path.join(BASE_DIR, "templates")

    os.makedirs(DATA_DIR, exist_ok=True)


path = Path()


class Settings(BaseSettings):
    # Secret keys and API keys
    JWT_SECRET_KEY_LENGTH: int = 32  # Length of the JWT secret key
    JWT_SECRET_KEY: str = Field(description="JWT secret key", default=os.urandom(JWT_SECRET_KEY_LENGTH).hex())
    JWT_ALGORITHM: str = Field("HS256", description="JWT algorithm for signing tokens")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60 * 24 * 3, description="JWT token expiration time in minutes")
    HTTP_API_KEY: str = Field("123456", description="HTTP API key for authentication")
    API_KEY_PREFIX: str = Field("tsk", description="Prefix for API keys")

    # CORS settings
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl | str] = Field(
        ["*"], description="List of allowed CORS origins for the backend"
    )

    # Database settings
    DATABASE_URL: str = Field("sqlite+aiosqlite:///./data/taskaza.db", description="Database connection URL")

    # Email settings
    FRONTEND_ORIGIN: str = Field("http://localhost:3000", description="Frontend origin for CORS and email links")
    SMTP_HOST: str = Field("smtp.gmail.com", description="SMTP server host")
    SMTP_PORT: int = Field(587, description="SMTP server port")
    SMTP_USERNAME: str = Field("username", description="SMTP username")
    SMTP_PASSWORD: str = Field("password", description="SMTP password or app password")
    EMAIL_FROM: str = Field("Taskaza <noreply@taskaza.app>", description="Default 'from' email address")

    # Configuration for Pydantic settings
    model_config = SettingsConfigDict(env_prefix="TSKZ_", env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()

if __name__ == "__main__":
    # Debugging: Print the settings to verify they are loaded correctly
    from pprint import pprint

    pprint(path.model_dump(), width=120)  # Debug statement to verify settings loading
    pprint(settings.model_dump(), width=120)  # Debug statement to verify settings loading
