from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

FRONTEND_ORIGIN = "http://localhost:5173"

REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=REPO_ROOT / ".env", extra="ignore")

    database_url: str


settings = Settings()  # pyright: ignore[reportCallIssue]
