from models import Link
from datetime import datetime

def test_link_init():
    """Базовая инициализация модели Link."""
    link = Link(short_code="abc123", original_url="https://example.com")
    assert link.short_code == "abc123"
    assert link.original_url == "https://example.com"
    assert link.is_anonymous is True
    assert link.click_count == 0
    assert link.id is not None

def test_link_attributes():
    """Проверка атрибутов после изменения."""
    link = Link(short_code="test", original_url="https://test.com")
    link.click_count = 5
    link.last_used_at = datetime.now()
    assert link.click_count == 5
    assert link.last_used_at is not None
