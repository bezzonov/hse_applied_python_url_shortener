from models import Link
from datetime import datetime

def test_link_creation():
    link = Link(short_code="abc", original_url="https://example.com")
    assert link.short_code == "abc"
    assert link.is_anonymous is True

def test_link_attributes():
    link = Link(short_code="test", original_url="https://test.com")
    link.click_count = 10
    link.last_used_at = datetime.now()
    assert link.click_count == 10
