from fastapi import Cookie, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from starlette.templating import Jinja2Templates

from app.routers.user.crud import SessionCRUD
from database import SessionLocal


templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(session_id: str = Cookie(None), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    if session_id is None:
        raise credentials_exception

    user = SessionCRUD.get_user_from_session_auth(session_id, db)

    if user is None:
        raise credentials_exception

    return user
