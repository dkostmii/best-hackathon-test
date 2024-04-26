from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from pydantic import ValidationError
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
import starlette.status as status

from app.dependencies import auth_only, get_current_user, get_db, handle_400_errors, staff_only, templates
from app.routers.request_task.crud import PrioritiesCRUD, RequestTaskCRUD
from app.routers.request_task.schema import RequestTaskCreateSchema
from app.routers.user.model import User

request_task_router = APIRouter(
    prefix="/request-tasks",
    tags=["request-tasks"]
)


@request_task_router.get("/")
@staff_only
async def get_request_tasks(
    request: Request,
    page: int = Query(1, gt=0),
    limit: int = Query(10, gt=0),
    done_status: Optional[str] = Query(None),
    priority_id: Optional[int] = Query(None),
    text_search: Optional[str] = Query(None),
    sort_by_newest: Optional[bool] = Query(None),
    sort_by_oldest: Optional[bool] = Query(None),
    sort_by_ending: Optional[bool] = Query(None),
    reset_filters: Optional[bool] = Query(None),  # Додаємо параметр reset_filters
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    if reset_filters:  # Якщо reset_filters=True, то скидаємо всі фільтри
        done_status = None
        priority_id = None
        text_search = None
        sort_by_newest = None
        sort_by_oldest = None
        sort_by_ending = None

    if done_status is not None:
        done_status = done_status.lower()
        if done_status not in ['done', 'todo', 'all']:
            done_status = None

    request_tasks_result = RequestTaskCRUD.get_request_tasks(
        db,
        page,
        limit,
        done_status,
        priority_id,
        text_search,
        sort_by_newest,
        sort_by_oldest,
        sort_by_ending,
    )

    priorities = PrioritiesCRUD.get_priorities(db)

    return templates.TemplateResponse(
        "request_task/list.html",
        {
            "request": request,
            "request_tasks": {"pagination": request_tasks_result},
            "current_user": current_user,
            "filter": {
                "done_status": done_status if done_status is None else done_status.lower(),
                "text_search": text_search,
            },
            "sort": {
                "priority_id": priority_id,
            },
            "priorities": priorities,
        }
    )


@request_task_router.get("/create")
@auth_only
async def create_request_task_page(
        request: Request,
        db: Session = Depends(get_db),
        current_user: Optional[User] = Depends(get_current_user)
):
    priorities = PrioritiesCRUD.get_priorities(db)

    return templates.TemplateResponse(
        "request_task/create.html",
        {
            "request": request,
            "priorities": priorities,
            "current_user": current_user,
        },
    )


@request_task_router.post("/create")
@auth_only
async def create_request_task(
        request: Request,
        priority_id: int = Form(...),
        name: str = Form(...),
        description: str = Form(...),
        db: Session = Depends(get_db),
        current_user: Optional[User] = Depends(get_current_user)
):
    try:
        data = RequestTaskCreateSchema(priority_id=priority_id, name=name, description=description)
        request_task = RequestTaskCRUD.create_request_task(data, current_user, db)

    except (ValidationError, HTTPException) as e:
        return handle_400_errors(request, e, "request_task/create.html")

    else:
        return RedirectResponse(f"/request-tasks/{request_task.id}", status_code=303)


@request_task_router.get("/{pk}")
@auth_only
async def get_request_task(
        request: Request,
        pk: UUID,
        db: Session = Depends(get_db),
        current_user: Optional[User] = Depends(get_current_user)
):
    request_task = RequestTaskCRUD.get_request_task_by_id(pk, db)

    if request_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Request task with id {pk} does not exist")

    if not current_user.is_staff and request_task.creator.id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to access this page")

    return templates.TemplateResponse(
        "request_task/single.html",
        {
            "request": request,
            "request_task": request_task,
            "current_user": current_user,
        },
    )


@request_task_router.post("/{pk}/done")
@staff_only
async def done_request_task(
        pk: UUID,
        db: Session = Depends(get_db),
        current_user: Optional[User] = Depends(get_current_user)
):
    request_task = RequestTaskCRUD.get_request_task_by_id(pk, db)

    if request_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Request task with id {pk} does not exist")

    request_task = RequestTaskCRUD.done_request_task(request_task, db)

    return RedirectResponse(f"/request-tasks/{request_task.id}", status_code=303)
