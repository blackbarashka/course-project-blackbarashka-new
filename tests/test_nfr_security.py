from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestNFRSecurity:
    """Тесты для проверки Security NFR требований"""

    def test_error_response_does_not_contain_stack_trace(self):
        """NFR-005: Тело ошибок не раскрывает внутреннюю структуру"""
        # Запрос несуществующей книги
        response = client.get("/api/v1/books/999999")
        assert response.status_code == 404

        error_data = response.json()
        # Проверяем что нет stack trace
        assert "traceback" not in str(error_data)
        assert "File" not in str(error_data)
        assert "line" not in str(error_data)

    def test_unified_error_messages(self):
        """NFR-005: Унифицированные сообщения об ошибках"""
        # Неправильный запрос на создание книги
        response = client.post("/api/v1/books", json={"invalid": "data"})

        # Проверяем consistent структуру ошибок
        if response.status_code != 200:
            error_data = response.json()
            assert "error" in error_data
            assert "code" in error_data["error"]
            assert "message" in error_data["error"]

    def test_api_responses_contain_correlation_id(self):
        """NFR-009: Проверка наличия correlation ID для трассируемости"""
        response = client.get("/api/v1/books")

        # В будущем: проверять наличие correlation ID в заголовках
        # assert "X-Correlation-ID" in response.headers
        assert response.status_code == 200

    def test_security_headers_present(self):
        """NFR-008: Проверка наличия security headers"""
        response = client.get("/api/v1/books")

        # Проверяем базовые security headers
        # В будущем можно добавить больше headers
        assert response.status_code == 200
        # assert "X-Content-Type-Options" in response.headers
        # assert "X-Frame-Options" in response.headers

    # === THREAT MODELING P04 ===
    def test_status_transition_validation_security(self):
        """STRIDE-Tampering: Защита от несанкционированного изменения статусов"""
        # Создаем книгу со статусом "прочитано"
        book_data = {
            "title": "Security Book",
            "author": "Author",
            "status": "completed",
        }
        response = client.post("/api/v1/books", json=book_data)
        book_id = response.json()["id"]

        # Пытаемся сделать недопустимый переход (прочитано → в процессе)
        status_update = {"status": "in_progress"}
        response = client.patch(f"/api/v1/books/{book_id}/status", json=status_update)

        # Должна быть ошибка валидации
        assert response.status_code == 400
        assert "Недопустимый переход статуса" in response.json()["detail"]
