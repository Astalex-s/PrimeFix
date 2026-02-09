"""Зависимости для защиты роутов JWT-токеном."""
import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.auth.model import Admin
from backend.auth.repository import AdminRepository
from backend.auth.utils import decode_access_token
from backend.core.database import get_db

logger = logging.getLogger(__name__)

security = HTTPBearer()


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> Admin:
    """Получение текущего администратора из JWT-токена."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен авторизации не предоставлен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен авторизации",
            headers={"WWW-Authenticate": "Bearer"},
        )

    admin_id_str = payload.get("sub")
    if admin_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен: отсутствует ID администратора",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        admin_id = int(admin_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный формат ID администратора в токене",
            headers={"WWW-Authenticate": "Bearer"},
        )

    admin = AdminRepository.get_by_id(db, admin_id)
    if admin is None or not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Администратор не найден или неактивен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return admin
