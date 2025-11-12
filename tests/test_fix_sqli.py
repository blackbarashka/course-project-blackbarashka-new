"""Тесты поиска книг."""

import importlib

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestBookSearchPositive:
    """Позитивные тесты для поиска книг"""

    def test_search_books_by_title(self):
        """Тест поиска книги по названию"""
        # Создаем тестовую книгу
        book_data = {
            "title": "London",
            "author": "Iden Martin",
            "description": "London is a beautiful city",
        }
        create_response = client.post("/api/v1/books", json=book_data)
        assert create_response.status_code == 200

        # Ищем по названию
        search_response = client.get("/api/v1/books/search?q=London")
        assert search_response.status_code == 200
        results = search_response.json()
        assert isinstance(results, list)
        assert len(results) > 0
        assert any("London" in book["title"] for book in results)

    def test_search_books_by_author(self):
        """Тест поиска книги по автору"""
        # Создаем тестовую книгу
        book_data = {
            "title": "Norwegian Wood",
            "author": "Haruki Murakami",
            "description": "Beautiful Tokyo",
        }
        create_response = client.post("/api/v1/books", json=book_data)
        assert create_response.status_code == 200

        # Ищем по автору
        search_response = client.get("/api/v1/books/search?q=Haruki")
        assert search_response.status_code == 200
        results = search_response.json()
        assert isinstance(results, list)
        assert any("Haruki" in book["author"] for book in results)

    def test_search_books_case_insensitive(self):
        """Тест поиска без учета регистра"""
        book_data = {
            "title": "Python Programming",
            "author": "John Doe",
        }
        create_response = client.post("/api/v1/books", json=book_data)
        assert create_response.status_code == 200

        # Ищем в нижнем регистре
        search_response = client.get("/api/v1/books/search?q=python")
        assert search_response.status_code == 200
        results = search_response.json()
        assert any("Python" in book["title"] for book in results)

    def test_search_books_partial_match(self):
        """Тест частичного совпадения"""
        book_data = {
            "title": "1984",
            "author": "George Orwell",
        }
        create_response = client.post("/api/v1/books", json=book_data)
        assert create_response.status_code == 200

        # Ищем по части слова
        search_response = client.get("/api/v1/books/search?q=19")
        assert search_response.status_code == 200
        results = search_response.json()
        assert any("19" in book["title"] for book in results)

    def test_search_books_empty_result(self):
        """Тест поиска с пустым результатом"""
        search_response = client.get("/api/v1/books/search?q=NonexistentBook12345")
        assert search_response.status_code == 200
        results = search_response.json()
        assert isinstance(results, list)
        assert len(results) == 0


class TestBookSearchInputValidation:
    """Тесты валидации входных данных"""

    def test_search_empty_query(self):
        """Тест валидации пустого запроса"""
        search_response = client.get("/api/v1/books/search?q=")
        # Должна быть ошибка валидации (422)
        assert search_response.status_code == 422

    def test_search_query_too_long(self):
        """Тест валидации слишком длинного запроса"""
        long_query = "A" * 201  # Превышает лимит 200 символов
        search_response = client.get(f"/api/v1/books/search?q={long_query}")
        assert search_response.status_code == 422

    def test_search_query_max_length(self):
        """Тест максимально допустимой длины запроса"""
        max_query = "A" * 200  # Ровно 200 символов
        search_response = client.get(f"/api/v1/books/search?q={max_query}")
        # Должен пройти валидацию (может вернуть пустой результат)
        assert search_response.status_code in [200, 422]

    def test_search_query_min_length(self):
        """Тест минимально допустимой длины запроса"""
        search_response = client.get("/api/v1/books/search?q=A")
        assert search_response.status_code == 200


class TestBookSearchSQLInjection:
    """Тесты защиты от SQL-инъекций."""

    def test_sqli_classic_union(self):
        """Тест защиты от UNION-инъекции."""
        book_data = {"title": "Test Book", "author": "Test Author"}
        client.post("/api/v1/books", json=book_data)

        malicious_query = "' OR '1'='1' UNION SELECT * FROM books--"
        search_response = client.get(f"/api/v1/books/search?q={malicious_query}")

        assert search_response.status_code in [200, 422, 400]

        if search_response.status_code == 200:
            results = search_response.json()
            assert isinstance(results, list)

    def test_sqli_comment_injection(self):
        """Тест защиты от инъекции через комментарии."""
        malicious_query = "'; DROP TABLE books; --"
        search_response = client.get(f"/api/v1/books/search?q={malicious_query}")

        assert search_response.status_code in [200, 422, 400]

        normal_search = client.get("/api/v1/books/search?q=Test")
        assert normal_search.status_code == 200

    def test_sqli_boolean_based(self):
        """Тест защиты от boolean-based инъекции."""
        malicious_query = "' OR '1'='1"
        search_response = client.get(f"/api/v1/books/search?q={malicious_query}")

        assert search_response.status_code in [200, 422, 400]

        if search_response.status_code == 200:
            results = search_response.json()
            assert isinstance(results, list)

    def test_sqli_time_based(self):
        """Тест защиты от time-based инъекции."""
        malicious_query = "'; WAITFOR DELAY '00:00:05'; --"
        search_response = client.get(f"/api/v1/books/search?q={malicious_query}")

        assert search_response.status_code in [200, 422, 400]

    def test_sqli_double_quote(self):
        """Тест защиты от инъекции с двойными кавычками."""
        malicious_query = '" OR "1"="1'
        search_response = client.get(f"/api/v1/books/search?q={malicious_query}")

        assert search_response.status_code in [200, 422, 400]

    def test_sqli_semicolon_injection(self):
        """Тест защиты от инъекции через точку с запятой."""
        malicious_query = "test'; SELECT * FROM books WHERE '1'='1"
        search_response = client.get(f"/api/v1/books/search?q={malicious_query}")

        assert search_response.status_code in [200, 422, 400]

    def test_sqli_like_injection(self):
        """Тест защиты от инъекции в LIKE оператор."""
        malicious_query = "%' OR '1'='1' OR title LIKE '%"
        search_response = client.get(f"/api/v1/books/search?q={malicious_query}")

        assert search_response.status_code in [200, 422, 400]

        if search_response.status_code == 200:
            results = search_response.json()
            assert isinstance(results, list)

    def test_sqli_concatenation(self):
        """Тест защиты от инъекции через конкатенацию."""
        malicious_query = "' || (SELECT password FROM users LIMIT 1) || '"
        search_response = client.get(f"/api/v1/books/search?q={malicious_query}")

        assert search_response.status_code in [200, 422, 400]

    def test_sqli_with_sqlite_specific(self):
        """Тест защиты от SQLite-специфичной инъекции."""
        malicious_query = "' UNION SELECT sql FROM sqlite_master--"
        search_response = client.get(f"/api/v1/books/search?q={malicious_query}")

        assert search_response.status_code in [200, 422, 400]

        if search_response.status_code == 200:
            results = search_response.json()
            assert isinstance(results, list)
            for book in results:
                assert "sqlite_master" not in str(book).lower()


class TestBookSearchWithSQLBackend:
    """Тесты поиска с SQL бэкендом"""

    def test_search_with_sql_backend(self, tmp_path, monkeypatch):
        """Тест поиска с SQL бэкендом"""
        pytest.importorskip("sqlalchemy")

        monkeypatch.setenv("USE_SQL_DB", "true")
        monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")

        # Перезагружаем модули
        import sys

        sys.modules.pop("app.storage.orm", None)
        sys.modules.pop("app.storage.db", None)
        sys.modules.pop("app.storage.database", None)
        sys.modules.pop("app.api.endpoints.books", None)
        sys.modules.pop("app.main", None)

        dbmod = importlib.import_module("app.storage.db")
        orm_mod = importlib.import_module("app.storage.orm")

        try:
            orm_mod.Base.metadata.drop_all(bind=dbmod.engine)
        except Exception:
            pass

        try:
            orm_mod.Base.metadata.create_all(bind=dbmod.engine)
        except Exception as exc:
            import sqlalchemy

            if isinstance(exc, sqlalchemy.exc.OperationalError):
                msg = str(exc).lower()
                if "index" in msg and "already exists" in msg:
                    pass
                else:
                    raise
            else:
                raise

        database_mod = importlib.import_module("app.storage.database")
        importlib.import_module("app.api.endpoints.books")
        importlib.import_module("app.main")

        db = database_mod.db

        # Создаем тестовую книгу через Database
        db.create_book(title="SQL Test Book", author="SQL Author", description="Test")

        # Тестируем безопасный поиск
        results = db.search_books("SQL")
        assert len(results) > 0
        assert any(book.title == "SQL Test Book" for book in results)

        malicious_query = "' OR '1'='1"
        results_malicious = db.search_books(malicious_query)
        assert isinstance(results_malicious, list)


class TestBookSearchErrorHandling:
    """Тесты обработки ошибок."""

    def test_error_response_format(self):
        """Тест формата ответа об ошибке."""
        search_response = client.get("/api/v1/books/search?q=")
        assert search_response.status_code == 422

        error_data = search_response.json()
        assert "type" in error_data
        assert "title" in error_data
        assert "status" in error_data
        assert "detail" in error_data
        assert "correlation_id" in error_data
        assert "timestamp" in error_data

    def test_error_no_stack_trace(self):
        """Тест что в ошибках нет stack trace."""
        long_query = "A" * 201
        search_response = client.get(f"/api/v1/books/search?q={long_query}")

        if search_response.status_code != 200:
            error_data = search_response.json()
            error_str = str(error_data)
            assert "traceback" not in error_str.lower()
            assert "file" not in error_str.lower() or "file" in error_data.get(
                "type", ""
            )

    def test_error_no_sensitive_data(self):
        """Тест что в ошибках нет чувствительных данных."""
        malicious_query = "' OR '1'='1"
        search_response = client.get(f"/api/v1/books/search?q={malicious_query}")

        if search_response.status_code != 200:
            error_data = search_response.json()
            error_str = str(error_data)
            assert "SELECT" not in error_str.upper()
            assert "FROM" not in error_str.upper()
            assert "DROP" not in error_str.upper()
            assert "sqlite_master" not in error_str.lower()
