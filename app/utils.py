from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional
from app.config import settings
import os
from email.mime.text import MIMEText
import smtplib
from dotenv import load_dotenv

# 비밀번호 해시용 context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

# 비밀번호 해시

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# JWT 토큰 발급/검증

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def send_email_naver(to_email, subject, body):
    smtp_server = "smtp.naver.com"
    smtp_port = 587
    smtp_user = os.getenv("NAVER_EMAIL")
    smtp_password = os.getenv("NAVER_PASSWORD")
    if not smtp_user or not smtp_password:
        print("[이메일 발송 실패] 환경변수(NAVER_EMAIL, NAVER_PASSWORD) 미설정")
        return False
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, [to_email], msg.as_string())
        print(f"[이메일 발송 성공] {to_email}")
        return True
    except Exception as e:
        print(f"[이메일 발송 실패] {e}")
        return False 