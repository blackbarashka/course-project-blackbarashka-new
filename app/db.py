from typing import Generator

from app.storage.db import SessionLocal


def get_db() -> Generator:
    """Совместимый генератор сессий для зависимостей FastAPI.

    Этот модуль является шимом, перенаправляющим вызовы на `app.storage.db`.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
