from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/v1/books", tags=["books"])

# Временное хранилище в памяти (для демо)
books_db = []
current_id = 1


# Возращаем все книги из списка.
@router.get("/")
def get_books():
    """Получить список всех книг"""
    return books_db


# Looking for a book by id.
@router.get("/{book_id}")
def get_book(book_id: int):
    """Получить книгу по ID"""
    book = next((b for b in books_db if b["id"] == book_id), None)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


# Add a new book.
@router.post("/")
def create_book(book_data: dict):
    """Добавить новую книгу"""
    global current_id

    # Базовая валидация
    if not book_data.get("title") or not book_data.get("author"):
        raise HTTPException(status_code=422, detail="Title and author are required")

    new_book = {
        "id": current_id,
        "title": book_data["title"],
        "author": book_data["author"],
        "description": book_data.get("description"),
        "status": "to_read",
    }

    books_db.append(new_book)
    current_id += 1
    return new_book


# Updating info about the book.
@router.put("/{book_id}")
def update_book(book_id: int, book_data: dict):
    """Обновить информацию о книге"""
    book = next((b for b in books_db if b["id"] == book_id), None)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Обновляем поля
    if "title" in book_data:
        book["title"] = book_data["title"]
    if "author" in book_data:
        book["author"] = book_data["author"]
    if "description" in book_data:
        book["description"] = book_data["description"]

    return book


# Updating status.
@router.patch("/{book_id}/status")
def update_book_status(book_id: int, status_data: dict):
    """Изменить статус прочтения"""
    book = next((b for b in books_db if b["id"] == book_id), None)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if "status" not in status_data:
        raise HTTPException(status_code=422, detail="Status is required")

    valid_statuses = ["to_read", "in_progress", "completed"]
    if status_data["status"] not in valid_statuses:
        raise HTTPException(
            status_code=422, detail=f"Status must be one of: {valid_statuses}"
        )

    book["status"] = status_data["status"]
    return book


# Deleting the book.
@router.delete("/{book_id}")
def delete_book(book_id: int):
    """Удалить книгу"""
    global books_db

    book_index = next((i for i, b in enumerate(books_db) if b["id"] == book_id), None)
    if book_index is None:
        raise HTTPException(status_code=404, detail="Book not found")

    deleted_book = books_db.pop(book_index)
    return {"message": f"Book '{deleted_book['title']}' deleted successfully"}
