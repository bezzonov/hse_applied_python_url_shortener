from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from sqlalchemy import or_
import uuid

# Импорты в конце, чтобы избежать циклических зависимостей
from crud import create_link, get_link, delete_link, update_link, search_links, get_db
from database import SessionLocal
from models import Link

app = FastAPI(title="URL Shortener API")

class ShortenRequest(BaseModel):
    original_url: HttpUrl
    custom_alias: Optional[str] = None
    expires_at: Optional[datetime] = None

class UpdateRequest(BaseModel):
    original_url: HttpUrl

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/docs")
async def docs():
    return {"message": "API documentation at /docs"}

@app.post("/links/shorten")
async def shorten(request: ShortenRequest, db: Session = Depends(get_db)):
    try:
        link = create_link(
            str(request.original_url),
            request.custom_alias,
            request.expires_at
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
    try:
        # Простой запрос БЕЗ or_
        link = db.query(Link).filter(Link.short_code == short_code).first()
        if not link:
            raise HTTPException(status_code=404, detail="Link not found")

        return {
            "original_url": link.original_url,
            "created_at": str(link.created_at),
            "clicks": link.click_count or 0,
            "last_used_at": str(link.last_used_at) if link.last_used_at else None,
            "expires_at": str(link.expires_at) if link.expires_at else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/links/{short_code}")
async def delete_link_endpoint(short_code: str, db: Session = Depends(get_db)):
    delete_link(short_code, db=db)
    return {"message": "Link deleted"}

@app.put("/links/{short_code}")
async def update_link_endpoint(short_code: str, request: UpdateRequest, db: Session = Depends(get_db)):
    update_link(short_code, str(request.original_url), db=db)
    return {"message": "Link updated"}

@app.get("/links/search")
async def search_endpoint(original_url: str = Query(...), db: Session = Depends(get_db)):
    links = search_links(original_url, db=db)
    return [{"short_code": link.short_code} for link in links]
