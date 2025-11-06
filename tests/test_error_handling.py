from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestRFC7807ErrorHandling:
    """Тесты для RFC 7807 формата ошибок"""

    def test_rfc7807_error_format(self):
        """Тест формата ошибок по RFC 7807"""
        response = client.get("/api/v1/books/999999")

        assert response.status_code == 404
        error_data = response.json()

        # Проверяем обязательные поля RFC 7807
        assert "type" in error_data
        assert "title" in error_data
        assert "status" in error_data
        assert "detail" in error_data
        assert "instance" in error_data
        assert "correlation_id" in error_data
        assert "timestamp" in error_data

    def test_validation_error_format(self):
        """Тест формата ошибок валидации"""
        # Неправильные данные - пустой title
        book_data = {"title": "", "author": "Test Author"}  # Пустой title
        response = client.post("/api/v1/books", json=book_data)

        # Должна быть 422 ошибка (не 400)
        assert response.status_code == 422
        error_data = response.json()

        # Проверяем структуру ошибки RFC 7807
        assert "type" in error_data
        assert "title" in error_data
        assert "detail" in error_data
        assert "correlation_id" in error_data

    def test_correlation_id_present(self):
        """Тест наличия correlation_id во всех ошибках"""
        error_scenarios = [
            ("GET", "/api/v1/books/999999"),  # Not found
            ("POST", "/api/v1/books", {"invalid": "data"}),  # Validation error
            ("GET", "/nonexistent-endpoint"),  # 404
        ]

        for method, url, *data in error_scenarios:
            if method == "GET":
                response = client.get(url)
            elif method == "POST":
                response = client.post(url, json=data[0] if data else {})

            if response.status_code != 200:
                error_data = response.json()
                assert "correlation_id" in error_data
                # correlation_id должен быть UUID формата
                assert len(error_data["correlation_id"]) == 36

    def test_no_stack_trace_in_production(self):
        """Тест отсутствия stack trace в ошибках"""
        # Создаем ситуацию которая может вызвать внутреннюю ошибку
        # (в реальном приложении это может быть деление на ноль и т.д.)
        response = client.get("/health")  # Этот endpoint всегда работает

        # Для этого теста нужно создать специальный endpoint с ошибкой
        # Пока проверяем что в известных ошибках нет stack trace
        response = client.get("/api/v1/books/invalid_id_format")
        if response.status_code != 200:
            error_data = response.json()
            error_str = str(error_data)
            assert "traceback" not in error_str
            assert "File" not in error_str
