import random
import string
import hashlib
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from database import SessionLocal, rdb
from models import Link
import re

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_short_code(length=7):
    chars = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choice(chars) for _ in range(length))
        if not link_exists(code):
            return code

def link_exists(short_code: str) -> bool:
    return rdb.exists(f"link:{short_code}") or db.query(Link).filter(Link.short_code == short_code).first() is not None

def create_link(original_url: str, custom_alias: str = None, expires_at: datetime = None, user_id: str = None):
    db = next(get_db())

    link = Link(
        original_url=original_url,
        user_id=user_id,
        is_anonymous=user_id is None,
        expires_at=expires_at
    )

    if custom_alias:
        if not re.match(r'^[a-zA-Z0-9]{4,10}$', custom_alias):
            raise ValueError("Invalid alias format")
        if link_exists(custom_alias):
            raise ValueError("Alias already exists")
        link.short_code = custom_alias
    else:
        link.short_code = generate_short_code()

    db.add(link)
    db.commit()
    db.refresh(link)

    # Кэш в Redis на 1 час
    if not expires_at or expires_at > datetime.utcnow():
        rdb.setex(f"link:{link.short_code}", 3600, link.id)

    return link

def get_link(short_code: str, db: Session):
    # Проверяем Redis
    cached_id = rdb.get(f"link:{short_code}")
    if cached_id:
        link = db.query(Link).filter(Link.short_code == short_code).first()
        if link and (not link.expires_at or link.expires_at > datetime.utcnow()):
            link.click_count += 1
            link.last_used_at = datetime.utcnow()
            db.commit()
            return link

    link = db.query(Link).filter(
        Link.short_code == short_code,
        Link.deleted_at.is_(None),
        or_(Link.expires_at.is_(None), Link.expires_at > datetime.utcnow())
    ).first()

    if link:
        link.click_count += 1
        link.last_used_at = datetime.utcnow()
        db.commit()
        rdb.setex(f"link:{link.short_code}", 3600, link.id)

    return link

def def delete_link(short_code: str, user_id: str | None = None, db: Session | None = None)::
    rdb.delete(f"link:{short_code}")
    db.query(Link).filter(
        Link.short_code == short_code,
        or_(Link.user_id == user_id, and_(Link.is_anonymous == True, user_id.is_(None)))
    ).update({"deleted_at": datetime.utcnow()})
    db.commit()

def search_links(original_url: str, user_id: str = None, db: Session):
    query = db.query(Link).filter(Link.original_url == original_url)
    if user_id:
        query = query.filter(Link.user_id == user_id)
    return query.all()
