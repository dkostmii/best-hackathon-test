from urllib import request
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from pydantic import ValidationError
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse

from app.dependencies import get_current_user, get_db, handle_400_errors, templates
from app.routers.request_task.crud import RequestTaskCRUD
from app.routers.request_task.schema import RequestTaskCreateSchema, RequestTaskSchema
from app.routers.user.model import User

request_task_router = APIRouter()


@request_task_router.get("/request-tasks")
async def get_request_tasks(
        page: int = Query(1, gt=0),
        limit: int = Query(10, gt=0),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    if not current_user.is_staff:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to access this page")

    request_tasks = RequestTaskCRUD.get_request_tasks(db, page, limit)

    return templates.TemplateResponse(
        "request_task/create_request_task.html",
        {
            "request": request,
            "request_tasks": request_tasks,
        },
    )


@request_task_router.get("/request-task/{pk}")
async def get_request_task(
        pk: UUID,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> RequestTaskSchema:
    if not current_user.is_staff:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to access this page")

    request_task = RequestTaskCRUD.get_request_task_by_id(pk, db)

    return templates.TemplateResponse(
        "request_task/create_request_task.html",
        {
            "request": request,
            "request_task": request_task,
        },
    )

@request_task_router.get("/request-tasks/")
async def create_request_task_page(request: Request):
    return templates.TemplateResponse(
        "request_task/create_request_task.html",
        {
            "request": request,
        },
    )


@request_task_router.post("/request-tasks/")
async def create_request_task(
        request: Request,
        priority_id: int = Form(...),
        name: str = Form(...),
        description: str = Form(...),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    try:
        data = RequestTaskCreateSchema(priority_id=priority_id, name=name, description=description)
        request_task = RequestTaskCRUD.create_request_task(data, current_user, db)

    except (ValidationError, HTTPException) as e:
        return handle_400_errors(request, e, "request-tasks/create_request_task.html")

    else:
        return RedirectResponse(f"/request-tasks/{request_task.id}", status_code=303)
