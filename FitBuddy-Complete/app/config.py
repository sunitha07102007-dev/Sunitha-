from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    app_name: str = "FitBuddy"
    database_url: str = f"sqlite:///{(BASE_DIR / 'data' / 'fitbuddy.db').as_posix()}"
    gemini_api_key: str | None = None
    workout_model: str = "gemini-2.5-pro"
    nutrition_model: str = "gemini-2.5-flash"
    admin_token: str = "change-me"
    demo_mode: bool = True
    max_age: int = 100
    model_temperature: float = 0.7
    model_max_tokens: int = 5000
    model_timeout_seconds: int = 60
    model_fallback_to_demo: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def ai_enabled(self) -> bool:
        return bool(self.gemini_api_key) and not self.demo_mode

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
