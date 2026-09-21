from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    groq_api_key: str
    cache_dir: str = "./cache"
    allowed_origins: list[str] = ["http://127.0.0.1:5500", "http://localhost:5500"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()