"""실제 인증 정보나 dotenv를 읽지 않는 초기화 설정."""

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """초기화에서는 mock 모드만 허용한다."""

    model_config = SettingsConfigDict(env_prefix="ONBOARDING_", env_file=None, extra="ignore")
    mode: Literal["mock"] = "mock"
