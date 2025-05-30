from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from app.config import settings

DATABASE_URL = settings.database_url
SYNC_DATABASE_URL = settings.sync_database_url

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
    pool_size=5,           # 동시에 유지할 커넥션 수
    max_overflow=10,       # pool_size 초과시 임시로 생성할 커넥션 수
    pool_recycle=1800,     # 30분마다 커넥션 재생성(끊김 방지)
    pool_pre_ping=True,    # 커넥션 유효성 체크(끊긴 커넥션 자동 재연결)
)
sync_engine = create_engine(SYNC_DATABASE_URL, echo=True, future=True)

SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

Base = declarative_base() 