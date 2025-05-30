from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="이메일 주소", example="user@example.com")
    password: str = Field(..., description="비밀번호", example="testpass123")
    nickname: str = Field(..., description="닉네임", example="홍길동")

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="이메일 주소", example="user@example.com")
    password: str = Field(..., description="비밀번호", example="testpass123")

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    nickname: str
    created_at: datetime

    class Config:
        from_attributes = True

class ChatSessionCreate(BaseModel):
    title: str = Field(..., description="채팅 세션 제목", example="기후변화 QnA")

class ChatSessionResponse(BaseModel):
    id: int
    title: str
    created_at: datetime

    class Config:
        from_attributes = True

class ChatMessageCreate(BaseModel):
    session_id: int = Field(..., description="채팅 세션 ID", example=1)
    role: str = Field(..., description="메시지 역할 (user/assistant)", example="user")
    content: str = Field(..., description="메시지 내용", example="안녕하세요")

class ChatMessageResponse(BaseModel):
    id: int
    session_id: int
    user_id: int | None
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str