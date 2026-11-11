from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

FRONTEND_ORIGIN = "http://localhost:5173"

REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=REPO_ROOT / ".env", extra="ignore")

    database_url: str
    # Not secrets: where tokens come from and who they are for
    keycloak_issuer: str = "http://localhost:8080/realms/trading"
    api_audience: str = "trading-api"


settings = Settings()  # pyright: ignore[reportCallIssue]
