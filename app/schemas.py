from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    nickname: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    nickname: str
    created_at: str

    class Config:
        orm_mode = True

class ChatSessionCreate(BaseModel):
    title: str

class ChatSessionResponse(BaseModel):
    id: int
    title: str
    created_at: str

    class Config:
        orm_mode = True 