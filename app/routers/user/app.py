from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.routers.user.crud import UserCRUD

user_router = APIRouter()


@user_router.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = UserCRUD.get_users(db)
    return {"users": users}