from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    airouter_api_key: str = ""
    airouter_base_url: str = "https://api.airouter.in/v1"
    llm_model: str = "openai/gpt-6-luna"
    reasoning_effort: str = ""
    request_timeout: int = 180
    llm_max_attempts: int = 3
    demo_mode: bool = False
    output_dir: Path = BASE_DIR / "outputs"
    api_url: str = "http://127.0.0.1:8000"

    @field_validator("output_dir", mode="after")
    @classmethod
    def make_absolute(cls, value):
        value = Path(value)
        return value if value.is_absolute() else BASE_DIR / value


@lru_cache
def get_settings():
    return Settings()
