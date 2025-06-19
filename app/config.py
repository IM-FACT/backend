from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "climate-factcheck-backend"
    debug: bool = True

    # --- DB & Redis (환경변수에서 값을 주입받음) ---
    postgres_password: str
    database_url: str
    sync_database_url: str
    redis_url: str

    # --- JWT ---
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    
    # --- 외부 API 키 ---
    openai_api_key: str
    brave_ai_api_key: str
    google_api_key: str
    
    # --- 이메일 (선택) ---
    naver_email: str | None = None
    naver_password: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()