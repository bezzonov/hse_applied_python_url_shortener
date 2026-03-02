from fastapi import FastAPI, HTTPException, Depends, Query, status
from fastapi.security import HTTPBearer
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional
import uuid
from crud import (
    create_link, get_link, delete_link, update_link, search_links, get_db
)
from models import Link

app = FastAPI(title="URL Shortener API")
security = HTTPBearer()

class ShortenRequest(BaseModel):
    original_url: HttpUrl
    custom_alias: Optional[str] = None
    expires_at: Optional[datetime] = None

class UpdateRequest(BaseModel):
    original_url: HttpUrl

# Публичные эндпоинты
@app.post("/links/shorten")
async def shorten(request: ShortenRequest, db: Session = Depends(get_db)):
    try:
        # Для анонимных - None user_id
        link = create_link(
            str(request.original_url),
            request.custom_alias,
            request.expires_at,
            user_id=None  # TODO: добавить авторизацию
        )
        return {
            "short_url": f"http://localhost:8000/{link.short_code}",
            "short_code": link.short_code
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/{short_code}")
async def redirect_to_original(short_code: str, db: Session = Depends(get_db)):
    link = get_link(short_code, db)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return RedirectResponse(url=link.original_url)

@app.get("/links/{short_code}/stats")
async def get_stats(short_code: str, db: Session = Depends(get_db)):
    link = db.query(Link).filter(
        Link.short_code == short_code,
        Link.deleted_at.is_(None),
        or_(Link.expires_at.is_(None), Link.expires_at > datetime.utcnow())
    ).first()

    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    return {
        "original_url": link.original_url,
        "created_at": link.created_at,
        "clicks": link.click_count,
        "last_used_at": link.last_used_at,
        "expires_at": link.expires_at
    }

# Защищенные эндпоинты (требуют авторизации)
@app.delete("/links/{short_code}")
async def delete_link_endpoint(
    short_code: str,
    token: str = Depends(security),  # TODO: реальная авторизация
    db: Session = Depends(get_db)
):
    delete_link(short_code, user_id="temp_user_id", db=db)  # TODO: из токена
    return {"message": "Link deleted successfully"}

@app.put("/links/{short_code}")
async def update_link_endpoint(
    short_code: str,
    request: UpdateRequest,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    link = update_link(short_code, str(request.original_url), user_id="temp_user_id", db=db)
    return {"message": "Link updated successfully"}

@app.get("/links/search")
async def search_endpoint(
    original_url: str = Query(...),
    db: Session = Depends(get_db)
):
    links = search_links(original_url, db=db)
    return [{"short_code": link.short_code, "created_at": link.created_at} for link in links]

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
