from datetime import datetime
from typing import TypeVar, Generic
from dataclasses import dataclass
from uuid import UUID
import math

from sqlalchemy import asc, desc
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


class RequestTaskCRUD:
    @staticmethod
    def get_request_tasks(
            db: Session,
            page: int,
            limit: int,
            done_status: str | None,
            priority_id: int | None,
            text_search: str | None,
            sort_by_newest: bool | None,
            sort_by_oldest: bool | None,
            sort_by_ending: bool | None,
            creator_id: UUID | None = None,
    ):
        offset = (page - 1) * limit

        is_done = None

        if done_status == 'done':
            is_done = True
        elif done_status == 'todo':
            is_done = False

        tasks = db.query(RequestTask)
        tasks = tasks.filter(RequestTask.name.ilike(f"%{text_search}%")) if text_search is not None else tasks
        tasks = tasks.filter(RequestTask.is_done.is_(is_done)) if is_done is not None else tasks
        tasks = tasks.filter_by(creator_id=creator_id) if creator_id is not None else tasks
        tasks = tasks.order_by(desc(RequestTask.created_at)) if sort_by_newest else tasks
        tasks = tasks.order_by(asc(RequestTask.created_at)) if sort_by_oldest else tasks
        tasks = tasks.order_by(desc(RequestTask.ending_at)) if sort_by_ending else tasks
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
