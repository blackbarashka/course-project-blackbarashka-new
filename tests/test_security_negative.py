from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestSecurityNegative:
    """Негативные тесты безопасности"""

    def test_path_traversal_prevention(self):
        """Тест защиты от path traversal атак"""
        # Пытаемся сделать path traversal через параметры
        malicious_paths = [
            "../../etc/passwd",
            "..\\..\\windows\\system32\\config",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
        ]

        for path in malicious_paths:
            response = client.get(f"/api/v1/books/{path}")
            # Должна быть 404 или 422, но не 500 и не раскрытие информации
            assert response.status_code in [404, 422, 400]
            if response.status_code != 200:
                # Проверяем что нет деталей внутренней ошибки
                error_data = response.json()
                assert "traceback" not in str(error_data)

    def test_sql_injection_prevention(self):
        """Тест защиты от SQL инъекций"""
        sql_injection_attempts = [
            "'; DROP TABLE books; --",
            "' OR '1'='1",
            "'; EXEC xp_cmdshell('format c:'); --",
        ]

        for injection in sql_injection_attempts:
            book_data = {"title": injection, "author": "Test Author"}
            response = client.post("/api/v1/books", json=book_data)
            # Система не должна падать с 500 ошибкой
            assert response.status_code != 500
            # Должна быть либо успешная обработка, либо ошибка валидации
            assert response.status_code in [200, 422, 400]

    def test_xss_prevention(self):
        """Тест защиты от XSS атак"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert(1)>",
            "javascript:alert('XSS')",
        ]

        for payload in xss_payloads:
            book_data = {
                "title": "Normal Book",
                "author": "Normal Author",
                "description": payload,
            }
            response = client.post("/api/v1/books", json=book_data)
            # Система должна обработать запрос без падения
            assert response.status_code in [200, 422]

            if response.status_code == 200:
                # Получаем созданную книгу и проверяем что данные сохранились
                book_id = response.json()["id"]
                get_response = client.get(f"/api/v1/books/{book_id}")
                assert get_response.status_code == 200
                # Данные должны быть сохранены как есть (экранирование на фронтенде)

    def test_mass_assignment_prevention(self):
        """Тест защиты от mass assignment атак"""
        # Пытаемся установить поля которые не должны быть доступны
        malicious_data = {
            "title": "Test Book",
            "author": "Test Author",
            "id": 999,  # Пытаемся установить ID
            "created_at": "2020-01-01",  # Пытаемся установить дату создания
            "admin": True,  # Пытаемся установить привилегии
        }

        response = client.post("/api/v1/books", json=malicious_data)
        # Должен быть успешный ответ или ошибка валидации
        assert response.status_code in [200, 422]

        if response.status_code == 200:
            created_book = response.json()
            # Проверяем что системные поля не были перезаписаны
            assert created_book["id"] != 999  # ID должен быть сгенерирован системой
            assert "admin" not in created_book  # Лишние поля должны игнорироваться
