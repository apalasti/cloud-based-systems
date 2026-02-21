import logging
import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import settings
from app.models import Photo

logger = logging.getLogger(__name__)
UPLOAD_DIR = settings.get_upload_dir()
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB


def create_photo(db: Session, name: str, file_name: str, user_id: int | None) -> Photo:
    photo = Photo(name=name, file_name=file_name, user_id=user_id)
    db.add(photo)
    db.commit()
    db.refresh(photo)
    logger.info("Photo created: id=%s name=%s file_name=%s", photo.id, name, file_name)
    return photo


def delete_photo(db: Session, photo: Photo) -> None:
    full_path = UPLOAD_DIR / photo.file_name
    if full_path.exists():
        full_path.unlink()
    else:
        logger.warning("Photo file missing on delete: id=%s file_name=%s", photo.id, photo.file_name)
    db.delete(photo)
    db.commit()
    logger.info("Photo deleted: id=%s name=%s", photo.id, photo.name)


def save_upload_file(file_content: bytes, original_filename: str) -> str:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    ext = Path(original_filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        ext = ".jpg"
    unique_name = f"{uuid.uuid4().hex}{ext}"
    path = UPLOAD_DIR / unique_name
    path.write_bytes(file_content)
    logger.info("Upload file saved: %s (from %s)", unique_name, original_filename)
    return unique_name
