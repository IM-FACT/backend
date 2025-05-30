from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import router as main_router
from app.config import settings
from app.auth import router as auth_router
from app.chat import router as chat_router
from app.exception_handlers import http_exception_handler, validation_exception_handler, server_error_handler
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException
from app.logging_config import logger

app = FastAPI(title=settings.app_name, debug=settings.debug)

# CORS 설정 (프론트엔드와 연동을 위해 필요시 수정)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(main_router)
app.include_router(auth_router)
app.include_router(chat_router)

# 로깅 설정 (이미 app/logging_config.py에서 적용됨)
logger.info("IM.FACT 백엔드 서버 시작")

# 전역 예외처리 핸들러 등록
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, server_error_handler)