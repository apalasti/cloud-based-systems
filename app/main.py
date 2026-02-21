import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.logging_config import setup_logging
from app.routers import auth, pages, photos

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="Photo Gallery")

app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(photos.router)

upload_dir = settings.get_upload_dir()
if upload_dir.exists():
    app.mount("/static/uploads", StaticFiles(directory=str(upload_dir)), name="static")
    logger.info("Photo Gallery started; upload dir mounted at /static/uploads")
else:
    logger.warning("Upload dir %s missing; /static/uploads not mounted", upload_dir)
