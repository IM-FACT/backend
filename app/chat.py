from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.schemas import ChatSessionCreate, ChatSessionResponse, ChatMessageCreate, ChatMessageResponse
from app.models import ChatSession, ChatMessage
from app.auth import get_current_user
from app.db import SessionLocal
from typing import List
from datetime import datetime

router = APIRouter(prefix="/chat", tags=["chat"])

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.post("/sessions", response_model=ChatSessionResponse)
async def create_session(
    session_in: ChatSessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    new_session = ChatSession(
        user_id=current_user.id,
        title=session_in.title,
        created_at=datetime.utcnow()
    )
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
    return new_session

@router.get("/sessions", response_model=List[ChatSessionResponse])
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    result = await db.execute(select(ChatSession).where(ChatSession.user_id == current_user.id))
    sessions = result.scalars().all()
    return sessions

@router.post("/messages", response_model=ChatMessageResponse)
async def create_message(
    msg_in: ChatMessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    new_msg = ChatMessage(
        session_id=msg_in.session_id,
        user_id=current_user.id if msg_in.role == "user" else None,
        role=msg_in.role,
        content=msg_in.content,
        created_at=datetime.utcnow()
    )
    db.add(new_msg)
    await db.commit()
    await db.refresh(new_msg)
    return new_msg

@router.get("/messages", response_model=List[ChatMessageResponse])
async def list_messages(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # 세션 소유자 확인
    result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="세션 접근 권한이 없습니다.")
    result = await db.execute(select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at))
    messages = result.scalars().all()
    return messages 