from datetime import tzinfo

import pytz
from fastapi.security import APIKeyHeader
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    env: str = ''
    db_url: str = ''
    secret_key: str
    token_expire_seconds: int = 1800
    timezone: tzinfo = pytz.timezone('Asia/Tehran')
    login_path: str = 'auth/login'
    oauth2_scheme: APIKeyHeader = APIKeyHeader(name='X-API-Key')  # X-API-Key can be any arbitrary name
    auth_route_prefix: str = '/auth'

    model_config = SettingsConfigDict(env_file="envs/.env")


def make_settings(env_file: str = None):
    global settings
    if settings is None:
        settings = Settings(_env_file=env_file) if env_file else Settings()
        print('settings loaded for env:', settings.env)


settings: Settings | None = None

