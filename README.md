# IM.FACT Backend - FastAPI

IM.FACT 서비스의 백엔드 API 서버입니다. 
사용자의 질문을 입력받아 응답을 반환하며, 추후 RAG(검색증강생성) 및 AI 기능이 통합될 예정입니다.

---

## 폴더 구조

```
backend/
├── app/                # FastAPI 라우터, 설정, 서비스 모듈 등
│   ├── __init__.py
│   ├── routers.py      # 엔드포인트 라우터 (health, /im-fact/ask 등)
│   ├── config.py       # 환경변수 및 설정 관리
│   ├── db.py           # DB 연결 및 세션 관리
│   └── models.py       # ORM 모델 정의
├── main.py             # FastAPI 앱 엔트리포인트
├── requirements.txt    # 의존성 패키지 목록
├── README.md           # 백엔드 설명 파일
├── alembic/            # DB 마이그레이션 관리 폴더
│   └── versions/       # 마이그레이션 이력 (반드시 git에 포함)
├── alembic.ini         # alembic 설정 파일
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
   - Swagger 문서: http://localhost:8000/docs

---

## 주요 엔드포인트

### POST /im-fact/ask
사용자의 질문을 받아 응답을 반환합니다. (현재는 더미 응답, 추후 RAG/AI 기능 통합 예정)

#### Request Body (JSON)
```json
{
  "content": "전기차는 친환경인가요?"
}
```

#### Response Body (JSON)
기본 구조(현재):
```json
{
  "content": "'전기차는 친환경인가요?'에 대한 테스트 응답입니다."
}
```

확장 구조(향후 RAG/AI 통합 시):
```json
{
  "content": "답변 텍스트",
  "sources": [
    {
      "name": "IPCC 제6차 평가보고서 (2021)",
      "url": "https://www.ipcc.ch/report/ar6/wg1/",
      "icon": "📄"
    }
  ],
  "citations": [
    {
      "text": "지구온난화를 1.5℃ 이내로 제한하기 위해서는...",
      "source_idx": 0
    }
  ],
  "meta": {
    "created_at": "2024-06-01T12:34:56",
    "confidence": 0.92
  }
}
```
- `sources`, `citations`, `meta` 등은 선택적 필드이며, RAG/AI 기능이 통합되면 프론트엔드에서 활용할 수 있습니다.

#### 상태 코드
- 200 : 요청이 성공적으로 처리됨
- 400 : 요청 JSON에 `content` 필드가 누락됨
- 500 : 서버 오류

---

## DB 설계 및 Alembic 마이그레이션
- SQLAlchemy ORM 기반 users, chat_sessions, chat_messages 테이블 설계
- Alembic으로 DB 마이그레이션 관리 (alembic/versions/ 폴더는 반드시 git에 포함)
- DB 유저/스키마 권한, 인코딩(UTF-8) 등 환경 주의

---

## .gitignore 규칙
- .env, *.env, venv, __pycache__, *.pyc 등 민감/불필요 파일 무시
- alembic/versions/는 반드시 git에 포함, alembic/README 등만 무시

---

## 개발 가이드
- FastAPI 최신 구조(모듈화, 의존성 주입, 환경설정 등) 적용
- 라우터, 서비스, 설정 등은 app/ 하위에 모듈화
- 향후 RAG/AI 기능은 app/services/ 등으로 확장 예정
- 테스트 및 문서화 권장
- **API 응답 구조는 향후 확장성을 고려해 설계**

---

## 향후 계획
- test_rag의 langchain 기반 RAG 기능 통합
- DB 연동, 인증, 로깅 등 기능 확장
- 프론트엔드와의 연동 및 end-to-end 테스트

---

## 커밋/버전관리 팁
- 커밋 시 alembic/versions/ 폴더, requirements.txt, .gitignore 등 변경사항 꼭 확인
- 민감정보(.env 등)는 절대 커밋하지 않기
