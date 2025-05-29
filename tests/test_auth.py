import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_register_and_login():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # 회원가입
        res = await ac.post("/auth/register", json={
            "email": "testuser@example.com",
            "password": "testpass123",
            "nickname": "테스트유저"
        })
        assert res.status_code == 200
        user = res.json()
        assert user["email"] == "testuser@example.com"

        # 로그인
        res = await ac.post("/auth/login", json={
            "email": "testuser@example.com",
            "password": "testpass123"
        })
        assert res.status_code == 200
        token = res.json()["access_token"]
        assert token

        # 내 정보 조회
        res = await ac.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        me = res.json()
        assert me["email"] == "testuser@example.com" 