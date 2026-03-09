import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from src.main import app

@pytest.fixture
def client():
    """Исправленный TestClient."""
    # Обход проблемы с версиями
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c

def test_health_check(client):
    """Тест /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@patch('src.crud.create_link')
def test_shorten_link(mock_create_link, client):
    """Тест создания короткой ссылки."""
    mock_link = Mock()
    mock_link.short_code = "abc123"
    mock_create_link.return_value = mock_link

    response = client.post("/links/shorten", json={
        "original_url": "https://example.com"
    })
    assert response.status_code == 200
    assert response.json()["short_code"] == "abc123"
