# IM.FACT Backend - FastAPI

IM.FACT 서비스의 백엔드 API 서버입니다.
- FastAPI 기반 RESTful API
- JWT 인증/회원 관리, 채팅 세션/메시지 관리
- Alembic 마이그레이션, 테스트 코드, 예외처리, Swagger(OpenAPI) 한글 문서화 지원

---

## 폴더 구조

```
backend/
├── app/                # FastAPI 라우터, 서비스, 설정, 유틸 등
│   ├── __init__.py
│   ├── routers.py      # 기본 엔드포인트(health 등)
│   ├── config.py       # 환경변수 및 설정
│   ├── db.py           # DB 연결 및 세션
│   ├── models.py       # ORM 모델
│   ├── schemas.py      # Pydantic 스키마(문서화 포함)
│   ├── utils.py        # 비밀번호 해시, JWT 등 유틸
│   ├── auth.py         # 인증/회원 관리 라우터
│   ├── chat.py         # 채팅 세션/메시지 라우터
│   ├── exception_handlers.py # 전역 예외처리
│   └── logging_config.py     # 로깅 설정
├── main.py             # FastAPI 앱 엔트리포인트
├── requirements.txt    # 의존성 패키지 목록
├── README.md           # 백엔드 설명 파일
├── alembic/            # DB 마이그레이션 폴더
│   └── versions/       # 마이그레이션 이력 (반드시 git에 포함)
├── alembic.ini         # alembic 설정 파일
├── .gitignore          # git 무시 규칙
├── tests/              # API 테스트 코드
│   ├── test_auth.py
│   └── test_chat.py
└── ...
```

---

## 실행 및 개발 환경 세팅

1. 의존성 설치
   ```bash
   pip install -r requirements.txt
   ```
2. 환경변수(.env) 파일 작성 (예시)
   ```env
   APP_NAME=climate-factcheck-backend
   DEBUG=True
   DATABASE_URL=postgresql+asyncpg://imfact_user:비밀번호@localhost:5432/imfact
   SYNC_DATABASE_URL=postgresql+psycopg2://imfact_user:비밀번호@localhost:5432/imfact
   ```
3. DB 마이그레이션 (최초 1회)
   ```bash
   alembic upgrade head
   ```
4. 서버 실행
   ```bash
   uvicorn main:app --reload
   ```
   - 기본 주소: http://localhost:8000
   - Swagger 문서: http://localhost:8000/docs (한글 설명/예시 제공)

---

## 주요 기능 및 API

### 1. 인증/회원 관리
- **회원가입**: `POST /auth/register`
- **로그인(JWT 토큰 발급)**: `POST /auth/login`
- **내 정보 조회**: `GET /auth/me` (토큰 필요)

### 2. 채팅 세션/메시지
- **세션 생성/조회/삭제**: `POST/GET/DELETE /chat/sessions`, `/chat/sessions/{session_id}`
- **메시지 저장/조회/삭제**: `POST/GET/DELETE /chat/messages`, `/chat/messages/{message_id}`

### 3. 헬스체크
- `GET /health`

---

## API 예시 (Swagger에서 한글 설명/예시 제공)

### 회원가입
```http
POST /auth/register
{
  "email": "user@example.com",
  "password": "testpass123",
  "nickname": "홍길동"
}
```

### 로그인
```http
POST /auth/login
{
  "email": "user@example.com",
  "password": "testpass123"
}
=> { "access_token": "...", "token_type": "bearer" }
```

### 내 정보 조회
```http
GET /auth/me
Authorization: Bearer {access_token}
```

### 채팅 세션 생성
```http
POST /chat/sessions
{
  "title": "기후변화 QnA"
}
```

### 메시지 저장
```http
POST /chat/messages
{
  "session_id": 1,
  "role": "user",
  "content": "안녕하세요"
}
```

---

## 테스트 코드 실행
```bash
python -m pytest tests/test_auth.py
python -m pytest tests/test_chat.py
```
- 회원가입/로그인/채팅 등 전체 API 자동 테스트

---

## 예외처리/로깅/문서화
- 모든 에러는 JSON 포맷으로 통일(`{"error": ...}`)
- 서버 시작/에러 등 주요 이벤트 로깅
- Swagger(OpenAPI)에서 한글 설명/예시 제공

---

## 개발/운영 주의사항
- 민감정보(.env 등)는 절대 커밋하지 않기
- alembic/versions/ 폴더는 반드시 git에 포함
- DB 유저/스키마 권한, 인코딩(UTF-8) 등 환경 주의

---

## 향후 계획
- RAG(검색증강생성) 기능 통합
- 프론트엔드와의 연동 및 end-to-end 테스트
- CI/CD, 배포 자동화 등
