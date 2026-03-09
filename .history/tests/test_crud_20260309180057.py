from unittest.mock import patch
import string

@patch('src.crud.rdb')
def test_generate_short_code(mock_rdb):
    mock_rdb.exists.return_value = False
    from src.crud import generate_short_code
    code = generate_short_code()
    assert len(code) == 7
    assert code.isalnum()
