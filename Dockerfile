# FastAPI 백엔드용 Dockerfile 예시
FROM python:3.10-slim

# 작업 디렉토리 생성 및 이동
WORKDIR /app

# 의존성 복사 및 설치
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 소스코드 복사
COPY . .

# Alembic 마이그레이션(컨테이너 시작 시 실행 권장)
# (docker-compose에서 entrypoint로 적용 가능)

# 기본 실행 명령 (uvicorn)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 