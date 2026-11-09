import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.config import settings
from app.models import User

ALGORITHM = "HS256"
REQUIRED_CLAIMS = ["iss", "sub", "exp", "jti", "role"]


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_token(user: User) -> str:
    payload = {
        "iss": settings.jwt_issuer,
        "sub": str(user.uid),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.token_minutes),
        "jti": str(uuid.uuid4()),
        "role": user.role.value,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[ALGORITHM],
        issuer=settings.jwt_issuer,
        options={"require": REQUIRED_CLAIMS},
    )