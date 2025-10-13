from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_health_check_security():
    """Тест security health check"""
    response = client.get("/health")
    assert response.status_code == 200

    # Проверяем что health endpoint не раскрывает чувствительную информацию
    health_data = response.json()
    assert "status" in health_data
    # Не должно быть чувствительных данных
    sensitive_keys = ["database_url", "secret_key", "password"]
    for key in sensitive_keys:
        assert key not in health_data
