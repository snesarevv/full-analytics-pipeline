from pydantic_settings import BaseSettings
from pydantic import PostgresDsn
from functools import lru_cache
from pathlib import Path


class Settings(BaseSettings):
    APP_NAME: str = "analytics_api"
    API_V1_PREFIX: str = "/api/v1"
    DB_URL: str = "postgresql+psycopg://app:app@db:5432/appdb"
    AUTO_SEED: bool = True
    DATA_DIR: str = "/mnt/data"   # points to your uploaded CSVs by default
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
