from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.schemas import UserCreate, UserResponse, UserLogin
from app.models import User
from app.utils import hash_password, verify_password, create_access_token, decode_access_token
from app.db import SessionLocal
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
import secrets

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

@router.post("/register", response_model=UserResponse, summary="회원가입", description="이메일, 비밀번호, 닉네임을 입력받아 회원가입을 처리합니다.")
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

@router.post("/login", summary="로그인", description="이메일과 비밀번호로 로그인하여 JWT 토큰을 발급받습니다.")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user.email))
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=400, detail="존재하지 않는 이메일입니다.")
    if not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="비밀번호가 일치하지 않습니다.")

    token = create_access_token({"sub": str(db_user.id)})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse, summary="내 정보 조회", description="JWT 토큰을 이용해 내 정보를 조회합니다.")
async def read_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/forgot-password", summary="비밀번호 찾기", description="이메일로 비밀번호 재설정 토큰을 발급합니다.")
async def forgot_password(req: UserCreate = None, db: AsyncSession = Depends(get_db)):
    from app.schemas import ForgotPasswordRequest
    if req is None:
        return {"detail": "요청 데이터가 필요합니다."}
    email = req.email
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="존재하지 않는 이메일입니다.")
    # 토큰 생성 및 만료시간(30분) 저장
    token = secrets.token_urlsafe(32)
    user.reset_token = token
    user.reset_token_expire = datetime.utcnow() + timedelta(minutes=30)
    await db.commit()
    # 이메일 발송 대신 print
    print(f"[비밀번호 재설정] 이메일: {email}, 토큰: {token}")
    return {"detail": "비밀번호 재설정 토큰이 이메일로 발송되었습니다."}

@router.post("/reset-password", summary="비밀번호 재설정", description="토큰과 새 비밀번호로 비밀번호를 재설정합니다.")
async def reset_password(req: UserCreate = None, db: AsyncSession = Depends(get_db)):
    from app.schemas import ResetPasswordRequest
    if req is None:
        return {"detail": "요청 데이터가 필요합니다."}
    token = req.token
    new_password = req.new_password
    result = await db.execute(select(User).where(User.reset_token == token))
    user = result.scalar_one_or_none()
    if not user or not user.reset_token_expire or user.reset_token_expire < datetime.utcnow():
        raise HTTPException(status_code=400, detail="유효하지 않거나 만료된 토큰입니다.")
    # 비밀번호 변경
    from app.utils import hash_password
    user.password_hash = hash_password(new_password)
    user.reset_token = None
    user.reset_token_expire = None
    await db.commit()
    return {"detail": "비밀번호가 성공적으로 변경되었습니다."} 