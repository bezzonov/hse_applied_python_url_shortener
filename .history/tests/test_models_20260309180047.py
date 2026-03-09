from src.models import Link
from datetime import datetime

def test_link_init():
    link = Link(short_code="abc123", original_url="https://example.com")
    assert link.short_code == "abc123"
    assert link.is_anonymous is True
    assert link.click_count == 0

def test_link_attributes():
    link = Link(short_code="test", original_url="https://test.com")
    link.click_count = 5
    assert link.click_count == 5
