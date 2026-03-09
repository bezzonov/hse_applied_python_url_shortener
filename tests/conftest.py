import pytest
import os
from unittest.mock import Mock
from pathlib import Path

@pytest.fixture(autouse=True)
def add_src_path(monkeypatch):
    """Добавляем src/ в PYTHONPATH автоматически."""
    src_path = Path(__file__).parent.parent / "src"
    monkeypatch.syspath_prepend(src_path)

@pytest.fixture
def mock_rdb():
    """Мок Redis."""
    rdb = Mock()
    rdb.exists.return_value = False
    rdb.get.return_value = None
    return rdb
