from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from app.user.app import user_router


base_app = FastAPI()
base_app.include_router(user_router)

templates = Jinja2Templates(directory="templates")


@base_app.get("/")
async def root(request: Request) -> templates.TemplateResponse:
    return templates.TemplateResponse(
        "base.html",
        {
            "request": request,
        },
    )

