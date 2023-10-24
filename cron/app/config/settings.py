from pydantic_settings import BaseSettings,SettingsConfigDict

__all__ = ("api_settings")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    TURSO_API_TOKEN: str
    TURSO_API_URL: str


api_settings =Settings(_env_file='.env', _env_file_encoding='utf-8')