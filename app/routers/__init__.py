from fastapi import APIRouter

from app.routers.user.app import user_router

app_router = APIRouter()

app_router.include_router(user_router)