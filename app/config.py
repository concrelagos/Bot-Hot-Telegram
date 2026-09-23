from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"

    telegram_bot_token: str
    telegram_webhook_secret: str = ""

    epague_api_key: str = ""
    epague_webhook_secret: str = ""
    epague_webhook_url: str = ""
    epague_shop_id: str = ""

    database_url: str = ""
    admin_telegram_id: int

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()