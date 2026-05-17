from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class ApiSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FRAM_", extra="ignore")

    api_token: str | None = None
    work_dir: Path = Path("tmp")


settings = ApiSettings()

