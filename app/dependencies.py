from typing import Any
from functools import wraps

from fastapi import Cookie, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.orm import Session
from starlette import status

from app.routers.user.crud import SessionCRUD
from app.routers.user.model import User
from database import SessionLocal


templates = Jinja2Templates(directory="templates")


def handle_400_errors(request: Request, errors: ValidationError | HTTPException, page: str, context: dict[str, Any] | None = None):
    errors = errors.errors() if isinstance(errors, ValidationError) else [errors.detail]

    default_context = {"request": request, "errors": errors}
    if context is None:
        context = default_context
    else:
        context = {**default_context, **context}

    return templates.TemplateResponse(
        name=page,
        context=context,
        status_code=400
    )


def auth_only(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        current_user = kwargs.get("current_user")

        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You must be logged in")

        return await func(*args, **kwargs)

    return wrapper


def staff_only(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        current_user = kwargs.get("current_user")

        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You must be logged in")

        if current_user.is_staff is False:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to access this page")

        return await func(*args, **kwargs)

    return wrapper


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
