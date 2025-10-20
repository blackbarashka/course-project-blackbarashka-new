import os
from datetime import datetime
from typing import List, Optional

# Флаг, указывающий, использовать ли SQLAlchemy-бэкенд
USE_SQL_DB = os.getenv("USE_SQL_DB", "false").lower() == "true"

if USE_SQL_DB:
    # Ленивые импорты, чтобы не требовать SQLAlchemy при обычной работе
    from app.storage.db import SessionLocal
    from app.storage.orm import BookORM


class InMemoryBook:
    def __init__(
        self,
        id: int,
        title: str,
        author: str,
        description: Optional[str] = None,
        status: str = "to_read",
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.status = status
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()


class Database:
    def __init__(self):
        if USE_SQL_DB:
            # SQL: операции выполняются через сессии SQLAlchemy
            self.backend = "sql"
        else:
            # In-memory: простой список объектов
            self.backend = "memory"
            self.books: List[InMemoryBook] = []
            self.current_id = 1

    def get_all_books(self) -> List[InMemoryBook]:
        if self.backend == "sql":
            with SessionLocal() as session:
                rows = session.query(BookORM).all()
                return [InMemoryBook(**r.to_domain()) for r in rows]
        return self.books

    def get_book_by_id(self, book_id: int) -> Optional[InMemoryBook]:
        if self.backend == "sql":
            with SessionLocal() as session:
                row = session.get(BookORM, book_id)
                return InMemoryBook(**row.to_domain()) if row else None
        return next((book for book in self.books if book.id == book_id), None)

    def create_book(self, title: str, author: str, description: Optional[str] = None):
        if self.backend == "sql":
            with SessionLocal() as session:
                orm = BookORM(title=title, author=author, description=description)
                session.add(orm)
                session.commit()
                session.refresh(orm)
                return InMemoryBook(**orm.to_domain())

        book = InMemoryBook(
            id=self.current_id, title=title, author=author, description=description
        )
        self.books.append(book)
        self.current_id += 1
        return book

    def update_book(self, book_id: int, **kwargs) -> Optional[InMemoryBook]:
        if self.backend == "sql":
            with SessionLocal() as session:
                orm = session.get(BookORM, book_id)
                if not orm:
                    return None
                for key, value in kwargs.items():
                    if value is not None and hasattr(orm, key):
                        setattr(orm, key, value)
                session.commit()
                session.refresh(orm)
                return InMemoryBook(**orm.to_domain())

        book = self.get_book_by_id(book_id)
        if not book:
            return None

        for key, value in kwargs.items():
            if value is not None and hasattr(book, key):
                setattr(book, key, value)

        book.updated_at = datetime.now()
        return book

    def delete_book(self, book_id: int) -> bool:
        if self.backend == "sql":
            with SessionLocal() as session:
                orm = session.get(BookORM, book_id)
                if orm:
                    session.delete(orm)
                    session.commit()
                    return True
                return False

        book = self.get_book_by_id(book_id)
        if book:
            self.books.remove(book)
            return True
        return False


# Глобальный экземпляр базы данных
db = Database()
