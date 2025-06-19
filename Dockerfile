# FastAPI 백엔드용 Dockerfile 
FROM python:3.10-slim

# 시스템 패키지 업데이트 및 Playwright 필요 패키지 설치
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    libnss3-dev \
    libatk-bridge2.0-dev \
    libdrm-dev \
    libxcomposite-dev \
    libxdamage-dev \
    libxrandr-dev \
    libgbm-dev \
    libgtk-3-dev \
    libasound2-dev \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 생성 및 이동
WORKDIR /app

# 의존성 복사 및 설치
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Playwright 브라우저 설치
RUN playwright install chromium
RUN playwright install-deps chromium

# 소스코드 복사
COPY . .

# Alembic 마이그레이션(컨테이너 시작 시 실행 권장)
# (docker-compose에서 entrypoint로 적용 가능)

# 기본 실행 명령 (uvicorn)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 