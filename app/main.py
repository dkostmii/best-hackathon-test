from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from app.routers import app_router


base_app = FastAPI()
base_app.include_router(app_router)

templates = Jinja2Templates(directory="templates")


@base_app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        "base.html",
        {
            "request": request,
        },
    )
