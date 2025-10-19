from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestInputValidation:
    """Тесты для безопасной валидации входных данных (ADR-002)"""

    def test_input_sanitization(self):
        """Тест санитизации потенциально опасных входных данных"""
        malicious_inputs = [
            {
                "title": "Test<script>alert('xss')</script>",
                "author": "Test Author",
                "description": "Normal description",
            },
            {
                "title": "Book; DROP TABLE books; --",
                "author": "Author",
                "description": "SQL injection attempt",
            },
            {
                "title": "../../etc/passwd",
                "author": "Hacker",
                "description": "Path traversal attempt",
            },
        ]

        for book_data in malicious_inputs:
            response = client.post("/api/v1/books", json=book_data)
            # Система должна обрабатывать эти данные без падения
            assert response.status_code in [200, 422]
            if response.status_code == 200:
                # Проверяем что данные сохранились как есть (санитизация на уровне бизнес-логики)
                book_id = response.json()["id"]
                get_response = client.get(f"/api/v1/books/{book_id}")
                assert get_response.status_code == 200
                # Данные должны сохраниться без изменений
                assert get_response.json()["title"] == book_data["title"]

    def test_field_length_validation(self):
        """Тест валидации длины полей"""
        # Слишком длинный title
        long_title_book = {
            "title": "A" * 201,  # Превышает лимит 200 символов
            "author": "Test Author",
        }
        response = client.post("/api/v1/books", json=long_title_book)
        assert response.status_code == 422  # Должна быть ошибка валидации

        # Слишком длинный author
        long_author_book = {
            "title": "Normal Title",
            "author": "B" * 101,  # Превышает лимит 100 символов
        }
        response = client.post("/api/v1/books", json=long_author_book)
        assert response.status_code == 422

        # Слишком длинное description
        long_desc_book = {
            "title": "Normal Title",
            "author": "Normal Author",
            "description": "C" * 501,  # Превышает лимит 500 символов
        }
        response = client.post("/api/v1/books", json=long_desc_book)
        assert response.status_code == 422

    def test_required_fields_validation(self):
        """Тест валидации обязательных полей"""
        # Отсутствует title
        no_title_book = {"author": "Test Author"}
        response = client.post("/api/v1/books", json=no_title_book)
        assert response.status_code == 422

        # Отсутствует author
        no_author_book = {"title": "Test Title"}
        response = client.post("/api/v1/books", json=no_author_book)
        assert response.status_code == 422

        # Пустые поля
        empty_fields_book = {"title": "", "author": ""}
        response = client.post("/api/v1/books", json=empty_fields_book)
        assert response.status_code == 422

    def test_json_payload_size_limit(self):
        """Тест лимита размера JSON payload"""
        # Создаем очень большой payload
        large_payload = {
            "title": "Test Book",
            "author": "Test Author",
            "description": "X" * 1000000,  # 1MB+ данных
        }
        response = client.post("/api/v1/books", json=large_payload)
        # Должна быть ошибка - либо 422, либо 413 (Payload Too Large)
        assert response.status_code in [422, 413, 400]

    def test_content_type_validation(self):
        """Тест валидации Content-Type"""
        # Неправильный Content-Type
        response = client.post(
            "/api/v1/books",
            data='{"title": "Test", "author": "Test"}',
            headers={"Content-Type": "text/plain"},
        )
        assert response.status_code in [
            415,
            422,
            400,
        ]  # Unsupported Media Type или ошибка валидации
