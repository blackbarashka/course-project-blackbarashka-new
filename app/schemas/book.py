from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from ..models.book import BookStatus


class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, example="Clean Code")
    author: str = Field(..., min_length=1, max_length=100, example="Robert Martin")
    description: Optional[str] = Field(
        None, max_length=500, example="About writing clean code"
    )


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    description: Optional[str]
    status: BookStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BookStatusUpdate(BaseModel):
    status: BookStatus


class BookSearchQuery(BaseModel):
    """Схема для валидации поискового запроса"""

    q: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Поисковый запрос (название или автор книги)",
        example="Clean Code",
    )
