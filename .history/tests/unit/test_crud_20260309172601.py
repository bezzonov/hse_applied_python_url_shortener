import pytest
from unittest.mock import patch, Mock
import string
import random

@patch('crud.rdb')
@patch('crud.SessionLocal')
@patch('crud.link_exists')
def test_generate_short_code(mock_exists, mock_db, mock_rdb):
    from crud import generate_short_code
    code = generate_short_code()
    assert len(code) == 7
    assert code.isalnum()

def test_models_without_db():
    from models import Link
    # НЕ сохраняем в БД - только объект
    link = Link(short_code="test", original_url="https://test.com")
    assert link.short_code == "test"
    assert link.click_count == 0
