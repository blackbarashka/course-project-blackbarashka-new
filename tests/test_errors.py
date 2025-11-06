from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_not_found_item():
    """Тест обработки 404 ошибок"""
    r = client.get("/items/999")
    assert r.status_code == 404
    # Проверяем новый формат RFC 7807
    error_data = r.json()
    assert "type" in error_data
    assert "title" in error_data
    assert "detail" in error_data


def test_validation_error():
    """Тест обработки ошибок валидации"""
    r = client.post("/items", params={"name": ""})
    assert r.status_code == 422
    # Проверяем новый формат RFC 7807
    error_data = r.json()
    assert "type" in error_data
    assert "title" in error_data
    assert "detail" in error_data
