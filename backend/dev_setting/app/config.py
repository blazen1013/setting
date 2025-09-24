# app/config.py
from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Colink Employee Service"
    database_url: str = "mysql+pymysql://user:password@localhost:3306/collab_platform"
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Pydantic v2: validator -> field_validator, pre=True -> mode="before"
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_origins(cls, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    # Pydantic v2 설정
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",        # 정의 안 된 환경변수 무시
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
