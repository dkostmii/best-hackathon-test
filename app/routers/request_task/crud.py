from datetime import datetime
from typing import TypeVar, Generic
from dataclasses import dataclass
from uuid import UUID
import math

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.routers.request_task.model import Priority, RequestTask
from app.routers.request_task.schema import RequestTaskCreateSchema
from app.routers.user.model import User

T = TypeVar("T")


@dataclass
class PaginatedResult(Generic[T]):
    items: list[T]
    has_next: bool
    has_prev: bool
    current_page: int
    current_limit: int


PRIORITY_ORDER = {
    "lowest": 1,
    "low": 2,
    "medium": 3,
    "high": 4,
    "highest": 5
}


class RequestTaskCRUD:
    @staticmethod
    def get_request_tasks(
            db: Session,
            page: int,
            limit: int,
            is_done: bool | None,
            priority_id: int | None,
            text_search: str | None,
    ):
        offset = (page - 1) * limit

        tasks = db.query(RequestTask)
        tasks = tasks.filter(RequestTask.name.ilike(f"%{text_search}%")) if text_search is not None else tasks
        tasks = tasks.filter_by(is_done=is_done) if is_done is not None else tasks
        tasks = (
            tasks.join(Priority).order_by(desc(RequestTask.priority_id == priority_id)).all()
            if priority_id is not None
            else tasks.all()
        )

        task_count = len(tasks)
        page_count = int(math.ceil(task_count / limit))

        items = tasks[offset:offset + limit]

        return PaginatedResult(
            items=items,
            current_page=page,
            current_limit=limit,
            has_prev=page > 1,
            has_next=page < page_count
        )

    @staticmethod
    def get_request_task_by_id(pk: UUID, db: Session):
        return db.query(RequestTask).filter_by(id=pk).first()

    @staticmethod
    def create_request_task(data: RequestTaskCreateSchema, creator: User, db: Session):
        request_task = RequestTask(
            name=data.name,
            description=data.description,
            creator_id=creator.id,
            priority_id=data.priority_id,
        )
        db.add(request_task)
        db.commit()
        db.refresh(request_task)

        return request_task

    @staticmethod
    def done_request_task(request_task: RequestTask, db: Session):
        request_task.is_done = True
        request_task.done_at = datetime.now()
        db.commit()
        db.refresh(request_task)

        return request_task


class PrioritiesCRUD:
    @staticmethod
    def get_priorities(db: Session):
        return db.query(Priority).all()
