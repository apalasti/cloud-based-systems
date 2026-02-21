from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Photo, User
from app.services.photo import (
    create_photo,
    delete_photo,
    save_upload_file,
    MAX_UPLOAD_BYTES,
)

router = APIRouter(tags=["photos"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/upload")
def upload_form(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse(
        "upload.html", {"request": request, "current_user": current_user}
    )


@router.post("/upload")
def upload_photo(
    name: str = Form(max_length=40),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if len(name) > 40:
        raise HTTPException(status_code=400, detail="Name must be at most 40 characters")
    content_type = file.content_type or ""
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    content = file.file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File too large (max {MAX_UPLOAD_BYTES // (1024*1024)} MB)",
        )
    file_name = save_upload_file(content, file.filename or "image")
    create_photo(db, name=name, file_name=file_name, user_id=current_user.id)
    return RedirectResponse(url="/?flash=uploaded", status_code=303)


@router.delete("/photo/{photo_id}")
def delete_photo_api(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    delete_photo(db, photo)
    return {"ok": True}


@router.post("/photo/{photo_id}/delete")
def delete_photo_form(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    delete_photo(db, photo)
    return RedirectResponse(url="/?flash=deleted", status_code=303)
