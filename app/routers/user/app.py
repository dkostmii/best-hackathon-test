from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import JSONResponse

from app.dependencies import get_current_user, get_db
from app.routers.user.crud import UserCRUD, SessionCRUD
from app.routers.user.hashing import Hasher
from app.routers.user.model import User
from app.routers.user.schema import UserRegistrationSchema, UserSchema, UserLoginSchema

user_router = APIRouter()


@user_router.get("/users")
def get_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    users = UserCRUD.get_users(db)
    return {"users": users}


@user_router.post("/users/register", status_code=201)
def create_user(form_data: UserRegistrationSchema, db: Session = Depends(get_db)) -> UserSchema:
    user = UserCRUD.create_user(db, form_data)
    if user is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this username already exist")
    return user


@user_router.post("/users/login")
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


@user_router.post("/users/logout")
async def logout(
        response: Response,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    SessionCRUD.delete_all_user_auth_session(current_user, db)
    response.delete_cookie("session_id")
    return {"message": "Logged out successfully"}
