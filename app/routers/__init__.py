from fastapi import APIRouter, Request, Depends

from app.dependencies import templates, get_current_user, get_db
from app.routers.user.app import user_router
from app.routers.user.model import User
from app.routers.request_task.app import request_task_router

from app.routers.request_task.model import Priority

db = next(get_db())
no_priorities = db.query(Priority).count() == 0
if no_priorities:
    priorities = [
        Priority(name="P1"),
        Priority(name="P2"),
        Priority(name="P3")
    ]

    for priority in priorities:
        db.add(priority)
        db.commit()
        db.refresh(priority)


app_router = APIRouter()

app_router.include_router(user_router)
app_router.include_router(request_task_router)


@app_router.get("/")
async def root(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse(
        "base.html",
        {
            "request": request,
            "current_user": current_user
        },
    )
