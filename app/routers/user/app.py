from fastapi import APIRouter, Depends, Form, HTTPException, Response, Request
from pydantic import ValidationError
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import JSONResponse

from app.dependencies import get_current_user, get_db, templates
from app.routers.user.crud import UserCRUD, SessionCRUD
from app.routers.user.hashing import Hasher
from app.routers.user.model import User
from app.routers.user.schema import UserRegistrationSchema, UserLoginSchema

user_router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@user_router.get("/")
def get_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    users = UserCRUD.get_users(db)

    return {"users": users}


@user_router.get("/register", status_code=201)
def create_user(request: Request):
    return templates.TemplateResponse(
        "auth/register.html",
        {
            "request": request,
        },
    )


@user_router.post("/register", status_code=201)
def create_user(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        is_staff: bool = Form(...),
        db: Session = Depends(get_db)
):
    try:
        data = UserRegistrationSchema(username=username, password=password, is_staff=is_staff)

        user = UserCRUD.create_user(db, data)

        if user is False:
            raise HTTPException(status_code=400, detail="User with this username already exists")

    except ValidationError as e:
        errors = e.errors()
        messages = [error["msg"] for error in errors]

        return templates.TemplateResponse(
            name="auth/register.html",
            context={"request": request, "errors": messages},
            status_code=400
        )

    except HTTPException as e:
        return templates.TemplateResponse(
            name="auth/register.html",
            context={"request": request, "errors": [e.detail]},
            status_code=e.status_code
        )
    else:
        session_token = SessionCRUD.create_session_token(user, db)
        response = templates.TemplateResponse(
            "base.html",
            {"request": request, "error_message": "User created successfully"}
        )
        response.set_cookie(key="session_id", value=session_token)

        return response


@user_router.post("/login")
def login(form_data: UserLoginSchema, db: Session = Depends(get_db)):
    user = UserCRUD.get_user_by_username(db, form_data.username)

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this username does not exist")

    if not Hasher.verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password")

    session_token = SessionCRUD.create_session_token(user, db)
    response = JSONResponse({"message": "Logged in successfully"})
    response.set_cookie(key="session_id", value=session_token)

    return response


@user_router.post("/logout")
async def logout(
        response: Response,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    SessionCRUD.delete_all_user_auth_session(current_user, db)
    response.delete_cookie("session_id")

    return {"message": "Logged out successfully"}
