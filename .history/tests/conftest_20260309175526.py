import pytest
import os
from unittest.mock import Mock
import redis

@pytest.fixture
def mock_rdb():
    """Мок Redis для всех тестов."""
    rdb = Mock()
    rdb.exists.return_value = False
    rdb.get.return_value = None
    rdb.setex.return_value = True
    rdb.delete.return_value = 1
    return rdb

@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    """Мокаем окружение для тестов."""
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./test.db")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379")
