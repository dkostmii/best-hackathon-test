from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.routers.request_task.crud import RequestTaskCRUD

request_task_router = APIRouter()


@request_task_router.get("/request-tasks")
def get_request_tasks(db: Session = Depends(get_db)):
    request_tasks = RequestTaskCRUD.get_request_tasks(db)
    return {"request_tasks": request_tasks}
