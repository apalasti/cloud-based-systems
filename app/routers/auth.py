import logging

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import ACCESS_TOKEN_COOKIE, get_current_user_optional
from app.models import User
from app.services.auth import create_access_token, get_password_hash

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="app/templates")


@router.get("/register", response_class=HTMLResponse)
def register_form(request: Request, current_user: User | None = Depends(get_current_user_optional)):
    return templates.TemplateResponse("register.html", {"request": request, "current_user": current_user})


@router.post("/register")
def register(
    username: str = Form(),
    password: str = Form(),
    db: Session = Depends(get_db),
):
    if db.query(User).filter(User.username == username).first():
        logger.warning("Registration rejected: username already registered: %s", username)
        raise HTTPException(status_code=400, detail="Username already registered")
    user = User(username=username, hashed_password=get_password_hash(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(data={"sub": user.username})
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key=ACCESS_TOKEN_COOKIE, value=token, httponly=True, samesite="lax")
    logger.info("User registered: %s", username)
    return response


@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request, current_user: User | None = Depends(get_current_user_optional)):
    return templates.TemplateResponse("login.html", {"request": request, "current_user": current_user})


@router.post("/login")
def login(
    username: str = Form(),
    password: str = Form(),
    db: Session = Depends(get_db),
):
    from app.services.auth import verify_password

    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        logger.warning("Login failed for user: %s", username)
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = create_access_token(data={"sub": user.username})
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key=ACCESS_TOKEN_COOKIE, value=token, httponly=True, samesite="lax")
    logger.info("User logged in: %s", username)
    return response


@router.post("/logout")
def logout(current_user: User | None = Depends(get_current_user_optional)):
    if current_user:
        logger.info("User logged out: %s", current_user.username)
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(ACCESS_TOKEN_COOKIE)
    return response
