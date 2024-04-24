from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from starlette import status

from app.dependencies import get_current_user, get_db
from app.routers.request_task.crud import RequestTaskCRUD
from app.routers.request_task.schema import RequestTaskCreateSchema, RequestTaskSchema
from app.routers.user.model import User

request_task_router = APIRouter()


@request_task_router.get("/request-tasks")
def get_request_tasks(
        page: int = Query(1, gt=0),
        limit: int = Query(10, gt=0),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    if not current_user.is_staff:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to access this page")

    request_tasks = RequestTaskCRUD.get_request_tasks(db, page, limit)

    return {"request_tasks": request_tasks}


@request_task_router.get("/request-task/{pk}")
def get_request_task(
        pk: UUID,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> RequestTaskSchema:
    if not current_user.is_staff:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to access this page")

    request_tasks = RequestTaskCRUD.get_request_task_by_id(pk, db)

    return request_tasks


@request_task_router.post("/request-tasks")
def create_request_task(
        data: RequestTaskCreateSchema,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> RequestTaskSchema:
    request_task = RequestTaskCRUD.create_request_task(data, current_user, db)

    return request_task
