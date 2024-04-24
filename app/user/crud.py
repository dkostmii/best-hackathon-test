from sqlalchemy.orm import Session

from app.user.model import User


class UserCRUD:
    @staticmethod
    def get_users(db: Session):
        return db.query(User).all()
