import pytest
import requests
from unittest.mock import patch, Mock
from src.main import app

# Простой тест БЕЗ TestClient
def test_health_check():
    """Тест /health через requests."""
    response = requests.get("http://localhost:8000/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@patch('src.crud.create_link')
def test_shorten_link(mock_create_link):
    """Тест создания ссылки."""
    mock_link = Mock()
    mock_link.short_code = "abc123"
    mock_create_link.return_value = mock_link

    response = requests.post("http://localhost:8000/links/shorten", json={
        "original_url": "https://example.com"
    })
    assert response.status_code == 200
