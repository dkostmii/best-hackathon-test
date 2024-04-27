from typing import Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from pydantic import ValidationError
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
import starlette.status as status

from settings import MAPBOX
from app.dependencies import (
    auth_only,
    get_current_user,
    get_db,
    get_done_status,
    get_sort_by,
    handle_400_errors,
    staff_only,
    templates,
)
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
    sort_by: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """
    Retrieve a list of request tasks with optional filtering and pagination.
    """

    done_status = get_done_status(done_status)

    sort_by = get_sort_by(sort_by)

    request_tasks_result = RequestTaskCRUD.get_request_tasks(
        db,
        page,
        limit,
        done_status,
        priority_id,
        text_search,
        sort_by,
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
                "sort_by": sort_by,
            },
            "priorities": priorities,
            "current_datetime": datetime.now(),
            "mapbox": MAPBOX,
        }
    )


@request_task_router.get("/create")
@auth_only
async def create_request_task_page(
        request: Request,
        db: Session = Depends(get_db),
        current_user: Optional[User] = Depends(get_current_user)
):
    """
    Render a webpage containing a form to create a new request task.
    """

    priorities = PrioritiesCRUD.get_priorities(db)

    return templates.TemplateResponse(
        "request_task/create.html",
        {
            "request": request,
            "priorities": priorities,
            "current_user": current_user,
            "mapbox": MAPBOX,
        },
    )


@request_task_router.post("/create")
@auth_only
async def create_request_task(
        request: Request,
        priority_id: int = Form(...),
        name: str = Form(...),
        description: str = Form(...),
        ending_at: Optional[datetime] = Form(None),
        location_lng_lat: Optional[str] = Form(None),
        db: Session = Depends(get_db),
        current_user: Optional[User] = Depends(get_current_user)
):
    """
    Create a new request task based on form data.
    """

    try:
        if ending_at and ending_at < datetime.now():
            raise HTTPException(status_code=400, detail="Deadline cannot be in the past.")

        data = RequestTaskCreateSchema(
            priority_id=priority_id,
            name=name,
            description=description,
            ending_at=ending_at,
            location_lng_lat=location_lng_lat
        )

        request_task = RequestTaskCRUD.create_request_task(data, current_user, db)

    except (ValidationError, HTTPException) as e:
        priorities = PrioritiesCRUD.get_priorities(db)
        return handle_400_errors(
            request,
            e,
            "request_task/create.html",
            context={
                "priorities": priorities,
                "mapbox": MAPBOX,
                "form": {
                    "name": name,
                    "description": description,
                    "ending_at": ending_at,
                    "location_lng_lat": location_lng_lat,
                    "priority_id": priority_id,
                },
            }
        )

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
    """
    Retrieve details of a specific request task by its ID.
    """

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
            "current_datetime": datetime.now(),
            "mapbox": MAPBOX,
        },
    )


@request_task_router.post("/{pk}/done")
@staff_only
async def done_request_task(
        pk: UUID,
        db: Session = Depends(get_db),
        current_user: Optional[User] = Depends(get_current_user)
):
    """
    Mark a request task as completed.
    """

    request_task = RequestTaskCRUD.get_request_task_by_id(pk, db)

    if request_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Request task with id {pk} does not exist")

    request_task = RequestTaskCRUD.done_request_task(request_task, db)

    return RedirectResponse(f"/request-tasks/{request_task.id}", status_code=303)
