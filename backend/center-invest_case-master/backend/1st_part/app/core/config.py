from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "CentreInvest Simulator"
    app_env: str = "dev"
    database_url: str
    secret_key: str
    access_token_expire_minutes: int = 60 * 24
    allowed_origins: str = "*"
    rate_limit_per_minute: int = 120
    enable_rate_limit: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
