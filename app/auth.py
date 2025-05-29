from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.schemas import UserCreate, UserResponse, UserLogin
from app.models import User
from app.utils import hash_password, verify_password, create_access_token, decode_access_token
from app.db import SessionLocal
from datetime import datetime
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

router = APIRouter(prefix="/auth", tags=["auth"])

# DB 세션 Dependency
async def get_db():
    async with SessionLocal() as session:
        yield session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="인증 정보가 유효하지 않습니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        raise credentials_exception
    user_id = int(payload["sub"])
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # 이메일 중복 체크
    result = await db.execute(select(User).where(User.email == user.email))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="이미 가입된 이메일입니다.")

    hashed_pw = hash_password(user.password)
    new_user = User(
        email=user.email,
        password_hash=hashed_pw,
        nickname=user.nickname,
        created_at=datetime.utcnow()
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.post("/login")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user.email))
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=400, detail="존재하지 않는 이메일입니다.")
    if not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="비밀번호가 일치하지 않습니다.")

    token = create_access_token({"sub": str(db_user.id)})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_me(current_user: User = Depends(get_current_user)):
    return current_user 