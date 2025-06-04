# IM.FACT Backend

**IM.FACT**는 환경·기후 데이터 기반의 신뢰성 있는 정보 제공을 목표로 하는 RAG(검색증강생성) 기반 AI 서비스입니다. 이 백엔드는 FastAPI, PostgreSQL, Redis를 활용해 빠르고 확장성 높은 API를 제공합니다.

---

## 🏗️ 프로젝트 개요

- **목표**: 누구나 신뢰할 수 있는 환경·기후 정보를 쉽고 빠르게 얻을 수 있도록 지원
- **주요 기술**: FastAPI, SQLAlchemy, Alembic, Redis(Vector Search), JWT, Docker
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
├── Dockerfile          # 백엔드 앱용 Dockerfile
├── docker-compose.yml  # 전체 서비스 오케스트레이션
└── ...
```
> 각 디렉터리별 상세 설명은 코드 내 docstring 및 주석 참고

---

## 🚀 빠른 시작 (Docker Compose)

1. `.env` 파일 생성 (민감정보 분리)
   - 아래 예시 참고해 backend 디렉터리에 `.env` 파일을 만듭니다.
   - 이 파일은 git에 커밋되지 않으니, 팀 내부에서만 안전하게 공유하세요.

   ```env
   # .env 예시
   POSTGRES_PASSWORD=여기에_안전한_비밀번호_입력
   REDIS_URL=redis://redis:6379
   # 기타 환경변수 추가 가능
   ```

2. Docker Compose로 전체 서비스 실행
   ```bash
   docker compose up --build
   ```
   - FastAPI(8000), PostgreSQL(5432), Redis(6379) 컨테이너가 한 번에 실행됩니다.
   - DB 마이그레이션도 자동 적용됩니다.

3. API 문서 접속
   - http://localhost:8000/docs (Swagger UI)

---

## 🛡️ 환경 변수 및 보안 주의사항

- **모든 민감정보(비밀번호, 시크릿키 등)는 반드시 .env 파일에만 작성**
- `.env` 파일은 이미 `.gitignore`에 포함되어 있어 git에 노출되지 않음
- docker-compose.yml의 POSTGRES_PASSWORD 등은 .env에서 자동으로 불러옴
- 팀 외부에 .env 파일이 유출되지 않도록 주의

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

### docker-compose 예시 (redis, db 포함)

```yaml
version: '3.8'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: imfact
      POSTGRES_USER: imfact_user
      POSTGRES_PASSWORD: 비밀번호
    ports:
      - "5432:5432"
    volumes:
      - db_data:/var/lib/postgresql/data

  redis:
    image: redis:latest
    ports:
      - "6379:6379"
    command: ["redis-server", "--loadmodule", "/usr/lib/redis/modules/redisearch.so"] # Vector Search용

  backend:
    build: .
    command: uvicorn main:app --host 0.0.0.0 --port 8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db
      - redis

volumes:
  db_data:
```

---

## 🧪 테스트 및 품질 관리

- 자동화된 pytest 기반 테스트 제공
- 커버리지 측정 및 CI/CD 연동 권장
- 예외/로깅/문서화 일관성 유지

```bash
docker compose exec backend pytest
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

## 📎 참고: 로컬 설치법(비권장)

- Python, PostgreSQL, Redis 직접 설치 후 requirements.txt, alembic, uvicorn 등 수동 실행
- 환경별 의존성/버전 차이로 인한 문제 발생 가능성 높음
- 팀/운영 환경에서는 반드시 Docker 기반 사용 권장
