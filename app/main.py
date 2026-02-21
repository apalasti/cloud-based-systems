from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routers import auth, pages, photos

app = FastAPI(title="Photo Gallery")

app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(photos.router)

upload_dir = settings.get_upload_dir()
if upload_dir.exists():
    app.mount("/static/uploads", StaticFiles(directory=str(upload_dir)), name="static")
