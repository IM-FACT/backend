import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_chat_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 회원가입 및 로그인
        await ac.post("/auth/register", json={
            "email": "chatuser@example.com",
            "password": "chatpass123",
            "nickname": "채팅유저"
        })
        res = await ac.post("/auth/login", json={
            "email": "chatuser@example.com",
            "password": "chatpass123"
        })
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 세션 생성
        res = await ac.post("/chat/sessions", json={"title": "테스트 세션"}, headers=headers)
        assert res.status_code == 200
        session = res.json()
        session_id = session["id"]

        # 세션 목록 조회
        res = await ac.get("/chat/sessions", headers=headers)
        assert res.status_code == 200
        sessions = res.json()
        assert any(s["id"] == session_id for s in sessions)

        # 메시지 저장
        res = await ac.post("/chat/messages", json={
            "session_id": session_id,
            "role": "user",
            "content": "안녕하세요"
        }, headers=headers)
        assert res.status_code == 200
        msg = res.json()
        msg_id = msg["id"]

        # 메시지 목록 조회
        res = await ac.get(f"/chat/messages?session_id={session_id}", headers=headers)
        assert res.status_code == 200
        msgs = res.json()
        assert any(m["id"] == msg_id for m in msgs)

        # 메시지 삭제
        res = await ac.delete(f"/chat/messages/{msg_id}", headers=headers)
        assert res.status_code == 200

        # 세션 삭제
        res = await ac.delete(f"/chat/sessions/{session_id}", headers=headers)
        assert res.status_code == 200 