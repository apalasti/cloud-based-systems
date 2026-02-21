import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from app.models import Photo

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "static" / "uploads"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB


def create_photo(db: Session, name: str, file_path: str, user_id: int | None) -> Photo:
    photo = Photo(name=name, file_path=file_path, user_id=user_id)
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


def delete_photo(db: Session, photo: Photo) -> None:
    # file_path is stored as e.g. /static/uploads/abc.jpg
    rel = photo.file_path.replace("/static/uploads/", "").lstrip("/")
    full_path = UPLOAD_DIR / rel
    if full_path.exists():
        full_path.unlink()
    db.delete(photo)
    db.commit()


def save_upload_file(file_content: bytes, original_filename: str) -> str:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    ext = Path(original_filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        ext = ".jpg"
    unique_name = f"{uuid.uuid4().hex}{ext}"
    path = UPLOAD_DIR / unique_name
    path.write_bytes(file_content)
    return f"/static/uploads/{unique_name}"
