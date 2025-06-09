from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    openai_model: str = "gpt-3.5-turbo"
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    log_dir: str = "/app/logs"

    class Config:
        env_file = ".env"

settings = Settings()
