from functools import lru_cache
from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración centralizada leída desde variables de entorno y .env."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Base de datos
    database_url: str
    test_database_url: str = ""

    # JWT
    secret_key: str = Field(min_length=32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # CORS
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://biblioteca-frontend-mui3.onrender.com",
    ]

    # Entorno
    environment: Literal["dev", "test", "prod"] = "dev"

    # Cloudinary
    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
