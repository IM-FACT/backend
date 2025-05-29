from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "climate-factcheck-backend"
    debug: bool = True
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/imfact"  # 예시

    class Config:
        env_file = ".env"

settings = Settings() 