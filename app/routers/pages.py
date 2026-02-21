from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user_optional
from app.models import Photo, User

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def dashboard(
    request: Request,
    sort: str | None = None,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    query = db.query(Photo)
    if sort == "name":
        query = query.order_by(Photo.name)
    else:
        query = query.order_by(Photo.created_at.desc())
    photos = query.all()
    flash = request.query_params.get("flash")
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "photos": photos,
            "current_user": current_user,
            "sort": sort or "date",
            "flash": flash,
        },
    )


@router.get("/photo/{photo_id}", response_class=HTMLResponse)
def photo_detail(
    request: Request,
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return templates.TemplateResponse(
        "photo_detail.html",
        {"request": request, "photo": photo, "current_user": current_user},
    )
