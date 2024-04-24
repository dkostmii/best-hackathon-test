from fastapi import FastAPI

from app.routers import app_router


base_app = FastAPI()
base_app.include_router(app_router)
