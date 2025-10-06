from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestBooksAPI:
    """Тесты для API книг"""

    def test_get_books_empty(self):
        """Тест получения пустого списка книг"""
        response = client.get("/api/v1/books")
        assert response.status_code == 200
        assert response.json() == []  # Теперь должен возвращаться пустой список

    def test_create_book_success(self):
        """Тест успешного создания книги"""
        book_data = {
            "title": "Test Book",
            "author": "Test Author",
            "description": "Test Description",
        }
        response = client.post("/api/v1/books", json=book_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == book_data["title"]
        assert data["author"] == book_data["author"]
        assert data["status"] == "to_read"  # Статус по умолчанию
        assert "id" in data

    def test_get_book_by_id_success(self):
        """Тест получения книги по ID"""
        # Сначала создаем книгу
        book_data = {"title": "Test Book", "author": "Test Author"}
        create_response = client.post("/api/v1/books", json=book_data)
        book_id = create_response.json()["id"]

        # Потом получаем её
        response = client.get(f"/api/v1/books/{book_id}")
        assert response.status_code == 200
        assert response.json()["id"] == book_id

    def test_get_book_by_id_not_found(self):
        """Тест получения несуществующей книги"""
        response = client.get("/api/v1/books/999")
        assert response.status_code == 404

    def test_update_book_status(self):
        """Тест изменения статуса книги"""
        # Создаем книгу
        book_data = {"title": "Test Book", "author": "Test Author"}
        create_response = client.post("/api/v1/books", json=book_data)
        book_id = create_response.json()["id"]

        # Меняем статус
        response = client.patch(
            f"/api/v1/books/{book_id}/status", json={"status": "in_progress"}
        )

        assert response.status_code == 200
        assert response.json()["status"] == "in_progress"
