from __future__ import annotations

from datetime import timedelta
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        enable_decoding=False,
    )

    app_name: str = "Center-Invest Cyber Simulator Backend"
    environment: str = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    secret_key: str = "change-me-change-me-change-me-2026"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 14

    database_url: str = "sqlite+aiosqlite:///./data/center_invest.db"
    redis_url: str = "redis://redis:6379/0"
    leaderboard_cache_ttl_seconds: int = 60
    scenario_seed_path: str = str(Path(__file__).resolve().parents[1] / "data" / "scenarios.json")

    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    cors_origin_regex: str = r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, value: object) -> object:
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "prod", "production", "false", "0", "off", "no"}:
                return False
            if normalized in {"debug", "dev", "development", "true", "1", "on", "yes"}:
                return True
        return value

    @property
    def access_token_ttl(self) -> timedelta:
        return timedelta(minutes=self.access_token_expire_minutes)

    @property
    def refresh_token_ttl(self) -> timedelta:
        return timedelta(days=self.refresh_token_expire_days)


settings = Settings()
