"""Pydantic-схемы для авторизации администраторов."""
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class AdminLogin(BaseModel):
    """Схема для входа администратора."""

    login: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1)

    @field_validator("password")
    @classmethod
    def validate_password_length(cls, v: str) -> str:
        """Проверка длины пароля (bcrypt ограничение — 72 байта)."""
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Пароль слишком длинный (максимум 72 байта)")
        return v


class AdminRegister(BaseModel):
    """Схема для регистрации администратора."""

    login: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(..., description="Email администратора")
    password: str = Field(
        ..., min_length=6, description="Минимум 6 символов, максимум 72 байта"
    )
    password_confirm: str = Field(..., min_length=6, description="Подтверждение пароля")

    @field_validator("password", "password_confirm")
    @classmethod
    def validate_password_length(cls, v: str) -> str:
        """Проверка длины пароля (bcrypt ограничение — 72 байта)."""
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Пароль слишком длинный (максимум 72 байта)")
        return v

    @model_validator(mode="after")
    def passwords_match(self):
        """Проверка совпадения паролей."""
        if self.password != self.password_confirm:
            raise ValueError("Пароли не совпадают")
        return self


class TokenResponse(BaseModel):
    """Ответ с токеном доступа."""

    access_token: str
    token_type: str = "bearer"


class AdminResponse(BaseModel):
    """Ответ с информацией об администраторе."""

    id: int
    login: str
    email: str
    is_active: bool
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class AdminExistsResponse(BaseModel):
    """Ответ о наличии администраторов в системе."""

    exists: bool
    count: int
