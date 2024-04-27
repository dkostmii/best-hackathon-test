from fastapi import APIRouter, Request, Depends

from app.dependencies import templates, get_current_user
from app.routers.user.app import user_router
from app.routers.user.model import User
from app.routers.request_task.app import request_task_router


app_router = APIRouter()

app_router.include_router(user_router)
app_router.include_router(request_task_router)


@app_router.get("/")
async def root(request: Request, current_user: User = Depends(get_current_user)):
    """
    Render the root endpoint, displaying the base HTML template.
    """
    return templates.TemplateResponse(
        "base.html",
        {
            "request": request,
            "current_user": current_user
        },
    )
