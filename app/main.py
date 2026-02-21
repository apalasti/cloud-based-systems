from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import auth, pages, photos

app = FastAPI(title="Photo Gallery")

app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(photos.router)

static_dir = Path(__file__).resolve().parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
