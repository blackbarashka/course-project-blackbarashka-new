from datetime import datetime
from typing import List, Optional

from app.models.book import Book


# Временное хранилище в памяти
class Database:
    def __init__(self):
        self.books: List[Book] = []
        self.current_id = 1

    def get_all_books(self) -> List[Book]:
        return self.books

    def get_book_by_id(self, book_id: int) -> Optional[Book]:
        return next((book for book in self.books if book.id == book_id), None)

    def create_book(
        self, title: str, author: str, description: Optional[str] = None
    ) -> Book:
        book = Book(
            id=self.current_id, title=title, author=author, description=description
        )
        self.books.append(book)
        self.current_id += 1
        return book

    def update_book(self, book_id: int, **kwargs) -> Optional[Book]:
        book = self.get_book_by_id(book_id)
        if not book:
            return None

        for key, value in kwargs.items():
            if value is not None and hasattr(book, key):
                setattr(book, key, value)

        book.updated_at = datetime.now()
        return book

    def delete_book(self, book_id: int) -> bool:
        book = self.get_book_by_id(book_id)
        if book:
            self.books.remove(book)
            return True
        return False


# Глобальный экземпляр базы данных
db = Database()
