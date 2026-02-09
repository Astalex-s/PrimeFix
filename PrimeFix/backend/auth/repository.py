"""Репозиторий администраторов (CRUD)."""
from sqlalchemy.orm import Session

from backend.auth.model import Admin
from backend.auth.utils import get_password_hash, verify_password


class AdminRepository:
    """CRUD-операции для Admin."""

    @staticmethod
    def create(db: Session, login: str, email: str, password: str) -> Admin:
        """Создание нового администратора."""
        password_hash = get_password_hash(password)
        admin = Admin(login=login, email=email, password_hash=password_hash)
        db.add(admin)
        db.commit()
        db.refresh(admin)
        return admin

    @staticmethod
    def get_by_email(db: Session, email: str) -> Admin | None:
        """Получение администратора по email."""
        return db.query(Admin).filter(Admin.email == email).first()

    @staticmethod
    def get_by_id(db: Session, admin_id: int) -> Admin | None:
        """Получение администратора по ID."""
        return db.query(Admin).filter(Admin.id == admin_id).first()

    @staticmethod
    def get_by_login(db: Session, login: str) -> Admin | None:
        """Получение администратора по логину."""
        return db.query(Admin).filter(Admin.login == login).first()

    @staticmethod
    def authenticate(db: Session, login: str, password: str) -> Admin | None:
        """Аутентификация администратора."""
        admin = AdminRepository.get_by_login(db, login)
        if not admin:
            return None
        if not admin.is_active:
            return None
        if not verify_password(password, admin.password_hash):
            return None
        return admin

    @staticmethod
    def count(db: Session) -> int:
        """Подсчет количества администраторов."""
        return db.query(Admin).count()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[Admin]:
        """Получение всех администраторов."""
        return db.query(Admin).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, admin_id: int, **kwargs) -> Admin | None:
        """Обновление администратора."""
        admin = AdminRepository.get_by_id(db, admin_id)
        if not admin:
            return None
        if "password" in kwargs:
            kwargs["password_hash"] = get_password_hash(kwargs.pop("password"))
        for key, value in kwargs.items():
            if hasattr(admin, key):
                setattr(admin, key, value)
        db.commit()
        db.refresh(admin)
        return admin

    @staticmethod
    def delete(db: Session, admin_id: int) -> bool:
        """Удаление администратора."""
        admin = AdminRepository.get_by_id(db, admin_id)
        if not admin:
            return False
        db.delete(admin)
        db.commit()
        return True
