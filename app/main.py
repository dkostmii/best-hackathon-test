from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates


base_app = FastAPI()

templates = Jinja2Templates(directory="templates")


@base_app.get("/")
async def root(request: Request) -> templates.TemplateResponse:
    return templates.TemplateResponse(
        "base.html",
        {
            "request": request,
        },
    )

