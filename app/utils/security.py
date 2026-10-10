import secrets
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from app.config import get_settings

settings = get_settings()
ALGORITHM = "HS256"


def create_session_token(user_id: int, phone: str) -> str:
    expire = datetime.utcnow() + timedelta(days=settings.SESSION_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "phone": phone,
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_session_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def generate_otp(length: int = 6) -> str:
    return "".join([str(secrets.randbelow(10)) for _ in range(length)])
