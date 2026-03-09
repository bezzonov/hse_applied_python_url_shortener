from src.models import Link
from datetime import datetime

def test_link_init():
    link = Link(
        short_code="abc123",
        original_url="https://example.com",
        is_anonymous=True,
        click_count=0  
    )
    assert link.short_code == "abc123"
    assert link.is_anonymous is True
    assert link.click_count == 0