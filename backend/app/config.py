from functools import lru_cache
from typing import Any
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "AirVision India API"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True

    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    database_url: str = "postgresql+asyncpg://airvision:airvision_secret@localhost:5432/airvision_india"
    database_url_sync: str = "postgresql://airvision:airvision_secret@localhost:5432/airvision_india"

    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    cors_origins: str = "http://localhost:3000"

    models_dir: str = "models_store"
    data_dir: str = "data"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @model_validator(mode="before")
    @classmethod
    def assemble_db_urls(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Check database_url (async engine)
            db_url = data.get("database_url")
            if db_url and isinstance(db_url, str):
                if db_url.startswith("postgresql://"):
                    data["database_url"] = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
                
                # Derive database_url_sync if it's not set or starts with asyncpg
                db_sync = data.get("database_url_sync")
                if not db_sync or not isinstance(db_sync, str) or db_sync.startswith("postgresql+asyncpg://"):
                    ref_url = db_sync if db_sync else db_url
                    data["database_url_sync"] = ref_url.replace("postgresql+asyncpg://", "postgresql://", 1)

            # Check database_url_sync (sync engine)
            db_sync = data.get("database_url_sync")
            if db_sync and isinstance(db_sync, str) and db_sync.startswith("postgresql+asyncpg://"):
                data["database_url_sync"] = db_sync.replace("postgresql+asyncpg://", "postgresql://", 1)

        return data


@lru_cache
def get_settings() -> Settings:
    return Settings()
