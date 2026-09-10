from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TD SYNNEX Product Matcher"
    td_synnex_mode: str = "mock"
    td_synnex_api_base_url: str | None = None
    td_synnex_client_id: str | None = None
    td_synnex_client_secret: str | None = None
    td_synnex_api_token: str | None = None
    request_timeout_seconds: float = 15.0
    database_url: str = "sqlite:///./product_matcher.db"
    allowed_origins: str = "http://localhost:5173,http://localhost:8080"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def origins(self) -> list[str]:
        return [item.strip() for item in self.allowed_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

