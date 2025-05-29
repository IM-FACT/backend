from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import router as main_router
from app.config import settings
from app.auth import router as auth_router

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