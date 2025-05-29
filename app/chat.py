from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.schemas import ChatSessionCreate, ChatSessionResponse
from app.models import ChatSession
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