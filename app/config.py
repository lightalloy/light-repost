from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    bot_token: str
    channel_id: int
    vk_token: str
    vk_group_id: int
    bot_mode: Literal["polling", "webhook"] = "webhook"  # дефолт
    webhook_base_url: str | None = None
    webhook_secret: str | None = None
    webhook_host: str = "0.0.0.0"
    webhook_port: int = 8080
    webhook_path: str = "/webhook"
    force_ipv4: bool = False
settings = Settings()
