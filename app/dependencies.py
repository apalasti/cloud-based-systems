import logging

from fastapi import Cookie, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.services.auth import decode_access_token

security = HTTPBearer(auto_error=False)
logger = logging.getLogger(__name__)

# Cookie name for browser/SSR login (must match name used when setting cookie)
ACCESS_TOKEN_COOKIE = "access_token"


def _token_from_request(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    access_token: str | None = Cookie(default=None),
) -> str | None:
    if credentials is not None:
        return credentials.credentials
    return access_token


def get_current_user(
    token: str | None = Depends(_token_from_request),
    db: Session = Depends(get_db),
) -> User:
    if token is None:
        logger.warning("Auth failure: no token provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_access_token(token)
    if payload is None:
        logger.warning("Auth failure: invalid or expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username = payload.get("sub")
    if not username:
        logger.warning("Auth failure: token missing subject")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    # Don't necesserily query the db for the user
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        logger.warning("Auth failure: user not found for username=%s", username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    return user


def get_current_user_optional(
    token: str | None = Depends(_token_from_request),
    db: Session = Depends(get_db),
) -> User | None:
    if token is None:
        return None
    payload = decode_access_token(token)
    if payload is None:
        return None
    username = payload.get("sub")
    if not username:
        return None
    return db.query(User).filter(User.username == username).first()


def prefers_json(request: Request) -> bool:
    accept = request.headers.get("accept", "")
    return "application/json" in accept.lower()
