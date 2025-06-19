from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.schemas import ChatSessionCreate, ChatSessionResponse, ChatMessageCreate, ChatMessageResponse
from app.models import ChatSession, ChatMessage, User  # User import 추가
# from app.auth import get_current_user  # DEMO: 인증 제거
from app.db import SessionLocal
from typing import List
from datetime import datetime

router = APIRouter(prefix="/chat", tags=["chat"])

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.post("/sessions", response_model=ChatSessionResponse, summary="채팅 세션 생성", description="새로운 채팅 세션을 생성합니다.")
async def create_session(
    session_in: ChatSessionCreate,
    db: AsyncSession = Depends(get_db)
    # current_user=Depends(get_current_user)  # DEMO: 인증 제거
):
    # DEMO: id=1 유저가 없으면 자동 생성
    user = await db.get(User, 1)
    if not user:
        user = User(
            id=1,
            email="demo@imfact.com",
            password_hash="demo_hash",
            nickname="데모",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    new_session = ChatSession(
        user_id=1,  # DEMO: 기본 사용자 ID 사용
        title=session_in.title,
        created_at=datetime.utcnow()
    )
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
    return new_session

@router.get("/sessions", response_model=List[ChatSessionResponse], summary="채팅 세션 목록 조회", description="채팅 세션 목록을 조회합니다.")
async def list_sessions(
    db: AsyncSession = Depends(get_db)
    # current_user=Depends(get_current_user)  # DEMO: 인증 제거
):
    # DEMO: 모든 세션 반환 (사용자 필터링 제거)
    result = await db.execute(select(ChatSession))
    sessions = result.scalars().all()
    return sessions

@router.post("/messages", response_model=ChatMessageResponse, summary="채팅 메시지 저장", description="채팅 세션에 메시지를 저장합니다.")
async def create_message(
    msg_in: ChatMessageCreate,
    db: AsyncSession = Depends(get_db)
    # current_user=Depends(get_current_user)  # DEMO: 인증 제거
):
    new_msg = ChatMessage(
        session_id=msg_in.session_id,
        user_id=1 if msg_in.role == "user" else None,  # DEMO: 기본 사용자 ID 사용
        role=msg_in.role,
        content=msg_in.content,
        created_at=datetime.utcnow()
    )
    db.add(new_msg)
    await db.commit()
    await db.refresh(new_msg)
    return new_msg

@router.get("/messages", response_model=List[ChatMessageResponse], summary="채팅 메시지 목록 조회", description="특정 세션의 메시지 목록을 조회합니다.")
async def list_messages(
    session_id: int,
    db: AsyncSession = Depends(get_db)
    # current_user=Depends(get_current_user)  # DEMO: 인증 제거
):
    # DEMO: 세션 소유자 확인 제거
    result = await db.execute(select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at))
    messages = result.scalars().all()
    return messages

@router.delete("/sessions/{session_id}", summary="채팅 세션 삭제", description="특정 채팅 세션과 하위 메시지를 삭제합니다.")
async def delete_session(
    session_id: int,
    db: AsyncSession = Depends(get_db)
    # current_user=Depends(get_current_user)  # DEMO: 인증 제거
):
    result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
    # DEMO: 소유자 확인 제거
    # 세션의 메시지 모두 삭제
    await db.execute(ChatMessage.__table__.delete().where(ChatMessage.session_id == session_id))
    await db.delete(session)
    await db.commit()
    return {"detail": "세션 및 메시지 삭제 완료"}

@router.delete("/messages/{message_id}", summary="채팅 메시지 삭제", description="특정 메시지를 삭제합니다.")
async def delete_message(
    message_id: int,
    db: AsyncSession = Depends(get_db)
    # current_user=Depends(get_current_user)  # DEMO: 인증 제거
):
    result = await db.execute(select(ChatMessage).where(ChatMessage.id == message_id))
    msg = result.scalar_one_or_none()
    if not msg:
        raise HTTPException(status_code=404, detail="메시지를 찾을 수 없습니다.")
    # DEMO: 소유자 확인 제거
    await db.delete(msg)
    await db.commit()
    return {"detail": "메시지 삭제 완료"} 