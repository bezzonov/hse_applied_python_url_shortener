import pytest
import string
from unittest.mock import patch, Mock
from datetime import datetime

# Тестируем только чистые функции без БД
@patch('crud.rdb')
@patch('crud.link_exists')
def test_generate_short_code(mock_exists, mock_rdb):
    """Генерация короткого кода - длина 7 символов."""
    mock_exists.return_value = False
    from crud import generate_short_code
    code = generate_short_code()
    assert len(code) == 7
    assert code.isalnum()
    assert code.isascii()

# Мокируем link_exists для независимости
@patch('crud.link_exists')
def test_generate_short_code_collision(mock_exists):
    """Обработка коллизий при генерации."""
    mock_exists.side_effect = [True, False]  # Первая коллизия, вторая OK
    from crud import generate_short_code
    code = generate_short_code()
    assert len(code) == 7
    mock_exists.assert_called_once()
