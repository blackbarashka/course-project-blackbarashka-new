from datetime import datetime
from enum import Enum
from typing import Optional


class BookStatus(str, Enum):
    TO_READ = "to_read"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Book:
    def __init__(
        self,
        id: int,
        title: str,
        author: str,
        description: Optional[str] = None,
        status: BookStatus = BookStatus.TO_READ,
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

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
