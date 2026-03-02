from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional
import re
from crud import create_link, get_link, delete_link, search_links, get_db
from sqlalchemy.orm import Session

app = FastAPI(title="URL Shortener")

class ShortenRequest(BaseModel):
    original_url: HttpUrl
    custom_alias: Optional[str] = None
    expires_at: Optional[datetime] = None

@app.post("/links/shorten")
async def shorten(request: ShortenRequest):
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
async def redirect(short_code: str):
    db = next(get_db())
    link = get_link(short_code, db)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return RedirectResponse(url=link.original_url)

@app.get("/links/{short_code}/stats")
async def stats(short_code: str):
    db = next(get_db())
    link = get_link(short_code, db)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return {
        "original_url": link.original_url,
        "created_at": link.created_at,
        "clicks": link.click_count,
        "last_used_at": link.last_used_at,
        "expires_at": link.expires_at
    }

@app.delete("/links/{short_code}")
async def delete(short_code: str):
    db = next(get_db())
    delete_link(short_code, db=db)
    return {"message": "Link deleted"}

@app.put("/links/{short_code}")
async def update(short_code: str, new_url: str):
    db = next(get_db())
    link = db.query(Link).filter(Link.short_code == short_code).first()
    if not link:
        raise HTTPException(status_code=404)
    link.original_url = new_url
    db.commit()
    return {"message": "Link updated"}

@app.get("/links/search")
async def search(
    original_url: str = Query(...),
    db: Session = Depends(get_db)
):
    links = search_links(original_url, db=db)
    return links

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
