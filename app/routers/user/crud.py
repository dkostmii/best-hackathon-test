import secrets
from uuid import UUID

from sqlalchemy.orm import Session
from fastapi import Request
from starlette.templating import Jinja2Templates

from app.routers.user.hashing import Hasher
from app.routers.user.model import User, Session as SessionModel
from app.routers.user.schema import UserLoginSchema, UserRegistrationSchema


class UserCRUD:
    @staticmethod
    def get_user_by_id(pk: UUID, db: Session):
        return db.query(User).filter_by(id=pk).first()

    @staticmethod
    def get_users(db: Session):
        return db.query(User).all()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> User | None:
        return db.query(User).filter_by(username=username).first()

    @classmethod
    def create_user(cls, db: Session, data: UserRegistrationSchema):
        validation = cls.validate_user_data(db, data)

        if not validation:
            return False

        user = User(
            username=data.username,
            password=Hasher.get_password_hash(data.password),
            is_staff=data.is_staff,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @classmethod
    def validate_user_data(cls, db: Session, data: UserRegistrationSchema):
        user = cls.get_user_by_username(db, data.username)

        if user:
            return False

        return True

    @staticmethod
    def authenticate_user(data: UserLoginSchema, db: Session) -> User | bool:
        user = UserCRUD.get_user_by_username(db, data.username)

        if not user:
            return False

        if not Hasher.verify_password(data.password, user.password):
            return False

        return user

    @staticmethod
    def login_user_html(
            request: Request,
            user: User,
            db: Session,
            templates: Jinja2Templates,
            response_page: str = "base.html"
    ):
        session_token = SessionCRUD.create_session_token(user, db)
        response = templates.TemplateResponse(
            response_page,
            {"request": request}
        )
        response.set_cookie(key="session_id", value=session_token)

        return response


class SessionCRUD:
    @classmethod
    def create_session_token(cls, user: User, db: Session) -> str:
        session_token = secrets.token_urlsafe(50)
        cls.delete_all_user_auth_session(user, db)
        session_auth_model = SessionModel(session_token=session_token, user=user)
        db.add(session_auth_model)
        db.commit()

        return session_token

    @staticmethod
    def delete_all_user_auth_session(user: User, db: Session, ) -> None:
        db.query(SessionModel).filter_by(user=user).delete()
        db.commit()

    @staticmethod
    def get_user_from_session_auth(session_token: str, db: Session) -> User:
        session_auth = db.query(SessionModel).filter_by(session_token=session_token).first()

        if session_auth:
            return session_auth.user
