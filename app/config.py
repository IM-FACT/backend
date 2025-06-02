import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "climate-factcheck-backend"
    debug: bool = True
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/imfact"  # 예시
    sync_database_url: str = "postgresql+psycopg2://postgres:password@localhost:5432/imfact"  # 추가
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    openai_api_key: str
    redis_url: str = "redis://localhost:6379"  # Redis 설정 추가

    class Config:
        env_file = os.path.join(Path(__file__).parent.parent, ".env")

settings = Settings()