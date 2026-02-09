"""Утилиты для JWT-токенов и хеширования паролей."""
import logging
import os
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

logger = logging.getLogger(__name__)

# JWT-настройки
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 часа

# Ограничение bcrypt на длину пароля
_BCRYPT_MAX_BYTES = 72


def _truncate_password(password: str) -> bytes:
    """Обрезка пароля до максимальной длины bcrypt (72 байта)."""
    return password.encode("utf-8")[:_BCRYPT_MAX_BYTES]


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля по bcrypt-хешу."""
    try:
        return bcrypt.checkpw(
            _truncate_password(plain_password),
            hashed_password.encode("utf-8"),
        )
    except Exception:
        logger.exception("Password verification failed")
        return False


def get_password_hash(password: str) -> str:
    """Хеширование пароля с помощью bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(_truncate_password(password), salt)
    return hashed.decode("utf-8")


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Создание JWT-токена."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """Декодирование JWT-токена."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        logger.debug("JWT decode error", exc_info=True)
        return None
    except Exception:
        logger.exception("Unexpected error decoding token")
        return None
