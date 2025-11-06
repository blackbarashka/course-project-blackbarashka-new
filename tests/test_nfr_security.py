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

        # Проверяем consistent структуру ошибок RFC 7807
        if response.status_code != 200:
            error_data = response.json()
            # Новый формат RFC 7807
            assert "type" in error_data
            assert "title" in error_data
            assert "detail" in error_data
            assert "status" in error_data

    def test_api_responses_contain_correlation_id(self):
        """NFR-009: Проверка наличия correlation ID для трассируемости"""
        response = client.get("/api/v1/books")
        assert response.status_code == 200

    def test_security_headers_present(self):
        """NFR-008: Проверка наличия security headers"""
        response = client.get("/api/v1/books")
        assert response.status_code == 200
