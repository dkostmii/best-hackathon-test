from fastapi import APIRouter, Request

from app.dependencies import templates
from app.routers.user.app import user_router
from app.routers.request_task.app import request_task_router

app_router = APIRouter()

app_router.include_router(user_router)
app_router.include_router(request_task_router)


@app_router.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        "base.html",
        {
            "request": request,
        },
    )
