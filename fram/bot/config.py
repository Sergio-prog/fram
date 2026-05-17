from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FRAM_", extra="ignore")

    bot_token: str | None = None
    bot_mode: str = "polling"
    bot_webhook_url: str | None = None
    work_dir: Path = Path("tmp")


settings = BotSettings()
