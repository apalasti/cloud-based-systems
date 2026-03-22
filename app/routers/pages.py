from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_username_optional, prefers_json
from app.models import Photo

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def dashboard(
    request: Request,
    sort: str | None = None,
    db: Session = Depends(get_db),
    username: str | None = Depends(get_username_optional),
):
    query = db.query(Photo)
    if sort == "name":
        query = query.order_by(Photo.name)
    else:
        query = query.order_by(Photo.created_at.desc())
    photos = query.all()
    flash = request.query_params.get("flash")

    if prefers_json(request):
        return JSONResponse(
            content={
                "photos": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "file_name": p.file_name,
                        "created_at": p.created_at.isoformat(),
                        "user_id": p.user_id,
                    }
                    for p in photos
                ],
                "current_user": {
                    "username": username,
                }
                if username
                else None,
                "sort": sort or "date",
                "flash": flash,
            }
        )

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "photos": photos,
            "username": username,
            "sort": sort or "date",
            "flash": flash,
        },
    )


@router.get("/photo/{photo_id}", response_class=HTMLResponse)
def photo_detail(
    request: Request,
    photo_id: int,
    db: Session = Depends(get_db),
    username: str | None = Depends(get_username_optional),
):
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    if prefers_json(request):
        return JSONResponse(
            content={
                "photo": {
                    "id": photo.id,
                    "name": photo.name,
                    "file_name": photo.file_name,
                    "created_at": photo.created_at.isoformat(),
                    "user_id": photo.user_id,
                },
                "current_user": {
                    "username": username,
                }
                if username
                else None,
            }
        )

    return templates.TemplateResponse(
        "photo_detail.html",
        {"request": request, "photo": photo, "username": username},
    )
