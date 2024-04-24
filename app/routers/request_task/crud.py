from uuid import UUID

from sqlalchemy.orm import Session

from app.routers.request_task.model import RequestTask
from app.routers.request_task.schema import RequestTaskCreateSchema
from app.routers.user.model import User


class RequestTaskCRUD:
    @staticmethod
    def get_request_tasks(db: Session, page: int, limit: int):
        offset = (page - 1) * limit
        return db.query(RequestTask).offset(offset).limit(limit).all()

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
