from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Groq
    groq_api_key: str = "changeme"
    groq_model: str = "llama-3.3-70b-versatile"

    # SEO APIs
    serpapi_key: str = ""
    gbp_api_key: str = ""

    @field_validator("serpapi_key", mode="before")
    @classmethod
    def blank_placeholder_keys(cls, v: str) -> str:
        placeholders = {"your_serpapi_key_here", "changeme", "change-me", "your-key-here"}
        return "" if str(v).strip() in placeholders else v

    # Database
    database_url: str = "postgresql+asyncpg://seo:seo_pass@localhost/seo_bot"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # App
    secret_key: str = "change-me"
    environment: str = "development"
    debug: bool = True

    # CORS — stored as plain string, parsed to list
    allowed_origins_str: str = "http://localhost:3000"

    @property
    def allowed_origins(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins_str.split(",") if o.strip()]

    # Storage
    storage_backend: str = "local"
    reports_dir: str = "./reports"

    # Rate limiting
    max_runs_per_project_per_day: int = 10


settings = Settings()
