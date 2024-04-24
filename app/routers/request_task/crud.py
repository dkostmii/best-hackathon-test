from sqlalchemy.orm import Session

from app.routers.request_task.model import RequestTask


class RequestTaskCRUD:
    @staticmethod
    def get_request_tasks(db: Session):
        return db.query(RequestTask).all()
