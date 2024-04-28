from datetime import datetime
from typing import TypeVar, Generic
from dataclasses import dataclass
from uuid import UUID
import math

from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.routers.request_task.model import Priority, RequestTask
from app.routers.request_task.schema import RequestTaskCreateSchema, RequestTaskSchema
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
            sort_by: str | None,
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

        order_by_clauses = []

        if priority_id is not None:
            order_by_clauses.append(desc(RequestTask.priority_id == priority_id))

        if sort_by == 'newest':
            order_by_clauses.append(desc(RequestTask.created_at))
        elif sort_by == 'oldest':
            order_by_clauses.append(asc(RequestTask.created_at))
        elif sort_by == 'ending':
            order_by_clauses.append(asc(RequestTask.ending_at))

        tasks = (
            tasks.order_by(*order_by_clauses).all()
            if len(order_by_clauses) > 0
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
            ending_at=data.ending_at,
            location_lng_lat=data.location_lng_lat,
            is_done=False,
        )
        db.add(request_task)
        db.commit()
        db.refresh(request_task)

        return request_task

    @staticmethod
    def update_request_task(data: RequestTaskSchema, db: Session):
        task_in_db: RequestTask = db.query(RequestTask).filter_by(id=data.id).first()

        task_in_db.name = data.name
        task_in_db.description = data.description
        task_in_db.priority_id = data.priority_id
        task_in_db.location_lng_lat = data.location_lng_lat
        task_in_db.ending_at = data.ending_at

        db.commit()
        db.refresh(task_in_db)

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
