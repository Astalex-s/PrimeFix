"""Автоматические миграции при старте приложения."""
import logging

from sqlalchemy import text
from sqlalchemy.engine import Connection, Engine

from backend.auth.model import Admin
from backend.core.database import Base

logger = logging.getLogger(__name__)


def run_migrations(engine: Engine) -> None:
    """Применение миграций к базе данных.

    Выполняется при каждом запуске приложения; каждая миграция
    идемпотентна (IF NOT EXISTS / проверка перед изменением).
    """
    try:
        with engine.begin() as conn:
            _migrate_leads_table(conn)
            _migrate_admins_table(conn, engine)
    except Exception as e:
        logger.warning("Migration error (non-fatal): %s", e)


# ── Внутренние функции миграций ──────────────────────────────────────


def _migrate_leads_table(conn: Connection) -> None:
    """Добавление колонки service в таблицу leads."""
    conn.execute(
        text("ALTER TABLE leads ADD COLUMN IF NOT EXISTS service VARCHAR(255)")
    )


def _migrate_admins_table(conn: Connection, engine: Engine) -> None:
    """Добавление колонки email в таблицу admins."""
    table_exists = conn.execute(
        text(
            "SELECT EXISTS ("
            "  SELECT FROM information_schema.tables WHERE table_name = 'admins'"
            ")"
        )
    ).scalar()

    if not table_exists:
        return

    email_exists = (
        conn.execute(
            text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = 'admins' AND column_name = 'email'"
            )
        ).fetchone()
        is not None
    )

    if email_exists:
        _ensure_email_index(conn)
        return

    row_count = conn.execute(text("SELECT COUNT(*) FROM admins")).scalar()

    if row_count == 0:
        # Таблица пустая — пересоздаём с новой структурой
        conn.execute(text("DROP TABLE admins CASCADE"))
        Base.metadata.create_all(bind=engine, tables=[Admin.__table__])
    else:
        # Есть данные — добавляем колонку как nullable
        conn.execute(text("ALTER TABLE admins ADD COLUMN email VARCHAR(255)"))
        _ensure_email_index(conn)
        try:
            conn.execute(
                text("ALTER TABLE admins ADD CONSTRAINT admins_email_unique UNIQUE (email)")
            )
        except Exception:
            pass


def _ensure_email_index(conn: Connection) -> None:
    """Создание индекса для email, если его нет."""
    try:
        conn.execute(
            text("CREATE INDEX IF NOT EXISTS ix_admins_email ON admins(email)")
        )
    except Exception:
        pass
