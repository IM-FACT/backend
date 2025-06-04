# IM.FACT Backend

**IM.FACT**는 환경·기후 데이터 기반의 신뢰성 있는 정보 제공을 목표로 하는 RAG(검색증강생성) 기반 AI 서비스입니다. 이 백엔드는 FastAPI, PostgreSQL, Redis를 활용해 빠르고 확장성 높은 API를 제공합니다.

---

## 🏗️ 프로젝트 개요

- **목표**: 누구나 신뢰할 수 있는 환경·기후 정보를 쉽고 빠르게 얻을 수 있도록 지원
- **주요 기술**: FastAPI, SQLAlchemy, Alembic, Redis Stack(Vector Search), JWT, Docker
- **특징**
  - RAG 기반 실시간 답변 생성
  - 시멘틱 캐시/문서 벡터 검색으로 빠른 응답
  - Swagger(OpenAPI) 한글 문서화
  - 자동화된 테스트 및 마이그레이션

---

## 📂 폴더 구조

```
backend/
├── app/                # FastAPI 라우터, 서비스, 설정, 유틸
├── main.py             # FastAPI 앱 엔트리포인트
├── requirements.txt    # 의존성 패키지 목록
├── alembic/            # DB 마이그레이션 폴더
├── tests/              # API 테스트 코드
└── ...
```
> 각 디렉터리별 상세 설명은 코드 내 docstring 및 주석 참고

---

## 🚀 빠른 시작

### 1. 개발 환경 준비

- Python 3.8 이상
- PostgreSQL 12 이상
- Redis 8.0 이상 (Vector Search 필수)
- (권장) Docker, Docker Compose

### 2. 설치 및 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# .env 파일 작성 (예시 아래 참고)
cp .env.example .env

# DB 마이그레이션
alembic upgrade head

# 서버 실행
uvicorn main:app --reload
```
- 기본 주소: http://localhost:8000
- Swagger 문서: http://localhost:8000/docs

---

## ⚙️ 환경 변수 예시 (.env)

```env
APP_NAME=climate-factcheck-backend
DEBUG=True
DATABASE_URL=postgresql+asyncpg://imfact_user:비밀번호@localhost:5432/imfact
REDIS_URL=redis://localhost:6379
```

---

## 🔑 주요 기능 및 API

- **인증/회원 관리**: 회원가입, 로그인(JWT), 내 정보 조회
- **채팅 세션/메시지**: 세션 생성/조회/삭제, 메시지 저장/조회/삭제
- **RAG 기반 답변**: `/im-fact/ask`에서 시멘틱 캐시/문서 벡터 검색 기반 답변 제공
- **헬스체크**: `/health` 엔드포인트

> 모든 엔드포인트 및 예시는 Swagger UI에서 확인 가능

---

## 🧠 Redis 기반 RAG(검색증강생성) 구조

- **시멘틱 캐시**: 질문-답변 쌍을 임베딩 벡터로 Redis에 저장, 유사 질문 즉시 응답
- **문서 벡터 검색**: 근거 문서 임베딩을 Redis에 저장, 질문과 유사한 문서를 벡터 유사도로 검색

### Redis Stack 설치 예시

```bash
docker run -d -p 6379:6379 redis:latest
```

### 운영 팁

- Redis Stack(8.x 이상, Vector Search 필수) 사용 권장
- Redis 장애 시 fallback 정책(예: DB 직접 조회)도 고려
- .env 파일에 REDIS_URL 필수

---

## 🧪 테스트 및 품질 관리

- 자동화된 pytest 기반 테스트 제공
- 커버리지 측정 및 CI/CD 연동 권장
- 예외/로깅/문서화 일관성 유지

```bash
python -m pytest tests/
```

---

## 🛠️ 개발/운영 체크리스트

- 민감정보(.env 등)는 git에 커밋 금지
- alembic/versions/ 폴더는 반드시 버전 관리
- DB/Redis 권한 및 인코딩(UTF-8) 확인
- 신규 기능 추가 시 테스트/문서화 필수

---

## 🗺️ 향후 계획

- RAG 고도화 및 프론트엔드 실시간 연동
- 자동화된 배포/테스트 환경 구축
- 사용자 피드백 기반 기능 개선 및 보안 강화

---
