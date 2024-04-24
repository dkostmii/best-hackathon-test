from fastapi import Cookie, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.routers.user.crud import SessionCRUD
from app.routers.user.model import User
from database import SessionLocal


templates = Jinja2Templates(directory="templates")


def handle_400_errors(request: Request, errors: ValidationError | HTTPException, page: str):
    errors = errors.errors() if isinstance(errors, ValidationError) else [errors.detail]

    return templates.TemplateResponse(
        name=page,
        context={"request": request, "errors": errors},
        status_code=400
    )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(session_id: str = Cookie(None), db: Session = Depends(get_db)) -> User | None:
    if session_id is None:
        return None

    user = SessionCRUD.get_user_from_session_auth(session_id, db)

    if user is None:
        return None

    return user
