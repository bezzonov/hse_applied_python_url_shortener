# Исправленная версия CRUD.py
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
    # Только Redis для быстрой проверки
    return rdb.exists(f"link:{short_code}")

def create_link(original_url: str, custom_alias: str = None, expires_at: datetime = None, user_id: str = None):
    db = SessionLocal()
    try:
        # Проверяем custom_alias
        if custom_alias:
            if not re.match(r'^[a-zA-Z0-9]{4,10}$', custom_alias):
                raise ValueError("Invalid alias format")
            if link_exists(custom_alias):
                raise ValueError("Alias already exists")
            short_code = custom_alias
        else:
            short_code = generate_short_code()

        link = Link(
            short_code=short_code,
            original_url=original_url,
            user_id=user_id,
            is_anonymous=user_id is None,
            expires_at=expires_at
        )

        db.add(link)
        db.commit()
        db.refresh(link)

        # Кэшируем ID ссылки
        cache_ttl = 3600
        if expires_at and expires_at < datetime.utcnow():
            cache_ttl = 60  # короткий TTL для истекающих
        rdb.setex(f"link:{link.short_code}", cache_ttl, link.id)

        return link
    finally:
        db.close()

def get_link(short_code: str, db: Session):
    # Сначала Redis
    cached_id = rdb.get(f"link:{short_code}")
    if cached_id:
        link = db.query(Link).filter(Link.id == cached_id.decode()).first()
    else:
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
    return None

def delete_link(short_code: str, user_id: str | None = None, db: Session | None = None):
    if not db:
        db = SessionLocal()
        local_db = True
    else:
        local_db = False

    try:
        # Удаляем из Redis
        rdb.delete(f"link:{short_code}")

        # Soft delete с проверкой владельца
        query = db.query(Link).filter(
            Link.short_code == short_code,
            Link.deleted_at.is_(None)
        )
        if user_id:
            query = query.filter(
                or_(Link.user_id == user_id, and_(Link.is_anonymous == True, Link.user_id.is_(None)))
            )

        link = query.first()
        if link:
            link.deleted_at = datetime.utcnow()
            db.commit()
    finally:
        if local_db:
            db.close()

def update_link(short_code: str, new_url: str, user_id: str | None = None, db: Session | None = None):
    if not db:
        db = SessionLocal()
        local_db = True
    else:
        local_db = False

    try:
        query = db.query(Link).filter(
            Link.short_code == short_code,
            Link.deleted_at.is_(None)
        )
        if user_id:
            query = query.filter(
                or_(Link.user_id == user_id, and_(Link.is_anonymous == True, Link.user_id.is_(None)))
            )

        link = query.first()
        if not link:
            raise HTTPException(status_code=404, detail="Link not found or access denied")

        link.original_url = new_url
        db.commit()

        # Обновляем кэш
        rdb.setex(f"link:{short_code}", 3600, link.id)
        return link
    finally:
        if local_db:
            db.close()

def search_links(original_url: str, user_id: str = None, db: Session | None = None):
    if not db:
        db = SessionLocal()
        local_db = True
    else:
        local_db = False

    try:
        query = db.query(Link).filter(
            Link.original_url == original_url,
            Link.deleted_at.is_(None),
            or_(Link.expires_at.is_(None), Link.expires_at > datetime.utcnow())
        )
        if user_id:
            query = query.filter(Link.user_id == user_id)
        return query.all()
    finally:
        if local_db:
            db.close()
