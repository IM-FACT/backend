from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import router as main_router
from app.config import settings
# from app.auth import router as auth_router  # DEMO: 인증 라우터 제거
from app.chat import router as chat_router
from app.exception_handlers import http_exception_handler, validation_exception_handler, server_error_handler
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException
from app.logging_config import logger
from app.redis.main_processor import MainProcessor
import sys
import asyncio

# Windows 환경에서 Playwright 호환성을 위한 이벤트 루프 정책 설정
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# 전역 MainProcessor 인스턴스
processor = None

app = FastAPI(title=settings.app_name, debug=settings.debug)

# CORS 설정 (프론트엔드와 연동을 위해 필요시 수정)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용 (운영 환경에서는 특정 도메인만 허용 권장)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(main_router)
# app.include_router(auth_router)  # DEMO: 인증 라우터 제거
app.include_router(chat_router)

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 MainProcessor 초기화"""
    global processor
    try:
        logger.info("MainProcessor 초기화 시작")
        processor = MainProcessor(redis_url=settings.redis_url)
        logger.info("MainProcessor 초기화 완료")
    except Exception as e:
        logger.error(f"MainProcessor 초기화 실패: {e}")
        raise e

# 로깅 설정 (이미 app/logging_config.py에서 적용됨)
logger.info("IM.FACT 백엔드 서버 시작")

# 전역 예외처리 핸들러 등록
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, server_error_handler)