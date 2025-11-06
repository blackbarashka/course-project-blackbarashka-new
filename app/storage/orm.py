from datetime import datetime
from typing import Dict

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.storage.db import Base

from ..models.book import BookStatus


class BookORM(Base):
    """ORM-модель книги для SQLAlchemy."""

    __tablename__ = "books"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default=BookStatus.TO_READ.value)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_domain(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
