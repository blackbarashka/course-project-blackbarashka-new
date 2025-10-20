import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

# Адрес БД
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./readinglist.db")

# Настройки двигателя SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    connect_args=(
        {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
    ),
)

# Фабрика сессий и базовый класс для моделей
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=Session
)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency для FastAPI: выдаёт сессию SQLAlchemy и закрывает её по завершении."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


__all__ = ["engine", "SessionLocal", "Base", "DATABASE_URL", "get_db"]
