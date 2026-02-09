"""API-роуты для авторизации администраторов."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.auth.dependencies import get_current_admin
from backend.auth.model import Admin
from backend.auth.repository import AdminRepository
from backend.auth.schema import (
    AdminExistsResponse,
    AdminLogin,
    AdminRegister,
    AdminResponse,
    TokenResponse,
)
from backend.auth.utils import create_access_token
from backend.core.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(credentials: AdminLogin, db: Session = Depends(get_db)):
    """Вход администратора."""
    admin = AdminRepository.authenticate(db, credentials.login, credentials.password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
        )
    access_token = create_access_token(data={"sub": str(admin.id)})
    return TokenResponse(access_token=access_token)


@router.post("/register", response_model=AdminResponse)
def register(data: AdminRegister, db: Session = Depends(get_db)):
    """Регистрация нового администратора (только если нет других админов)."""
    # Проверяем, есть ли уже администраторы
    admin_count = AdminRepository.count(db)
    if admin_count > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Регистрация недоступна. В системе уже есть администраторы.",
        )
    
    # Проверяем, не существует ли уже такой логин
    existing_admin = AdminRepository.get_by_login(db, data.login)
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Администратор с таким логином уже существует",
        )
    
    # Проверяем, не существует ли уже такой email
    existing_email = AdminRepository.get_by_email(db, data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Администратор с таким email уже существует",
        )
    
    admin = AdminRepository.create(db, data.login, data.email, data.password)
    return AdminResponse(
        id=admin.id,
        login=admin.login,
        email=admin.email,
        is_active=admin.is_active,
        created_at=admin.created_at,
    )


@router.get("/check-admin-exists", response_model=AdminExistsResponse)
def check_admin_exists(db: Session = Depends(get_db)):
    """Проверка наличия администраторов в системе."""
    count = AdminRepository.count(db)
    return AdminExistsResponse(exists=count > 0, count=count)


@router.get("/me", response_model=AdminResponse)
def get_current_admin_info(admin: Admin = Depends(get_current_admin)):
    """Получение информации о текущем администраторе."""
    return AdminResponse(
        id=admin.id,
        login=admin.login,
        email=admin.email,
        is_active=admin.is_active,
        created_at=admin.created_at,
    )
