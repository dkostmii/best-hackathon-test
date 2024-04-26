from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Form, Query, HTTPException, Response, Request
from pydantic import ValidationError
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse

from app.dependencies import auth_only, get_current_user, get_db, handle_400_errors, templates
from app.routers.user.crud import UserCRUD, SessionCRUD
from app.routers.user.model import User
from app.routers.user.schema import UserRegistrationSchema, UserLoginSchema
from app.routers.request_task.crud import RequestTaskCRUD

user_router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@user_router.get("/")
async def get_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    users = UserCRUD.get_users(db)

    return {"users": users}


@user_router.get("/register")
async def create_user_page(
        request: Request,
        is_staff: bool = Query(False),
        current_user: Optional[User] = Depends(get_current_user)
):
    if current_user:
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse(
        "auth/register.html",
        {
            "request": request,
            "form_defaults": {"is_staff": is_staff},
        },
    )


@user_router.post("/register")
async def create_user(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        is_staff: bool = Form(False),
        db: Session = Depends(get_db)
):
    try:
        data = UserRegistrationSchema(username=username, password=password, is_staff=is_staff)
        user = UserCRUD.create_user(db, data)

        if user is False:
            raise HTTPException(status_code=400, detail="User with this username already exists")

    except (ValidationError, HTTPException) as e:
        return handle_400_errors(request, e, "auth/register.html")

    else:
        response = UserCRUD.login_user_html(request, user, db, templates)
        return response


@user_router.get("/login")
async def login_page(request: Request, current_user: Optional[User] = Depends(get_current_user)):
    if current_user:
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse(
        "auth/login.html",
        {
            "request": request,
        },
    )


@user_router.post("/login")
async def login(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    try:
        form_data = UserLoginSchema(username=username, password=password)
        user = UserCRUD.authenticate_user(form_data, db)

        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")

    except (ValidationError, HTTPException) as e:
        return handle_400_errors(request, e, "auth/login.html")

    else:
        response = UserCRUD.login_user_html(request, user, db, templates)
        return response


@user_router.post("/logout")
@auth_only
async def logout(
        response: Response,
        current_user: Optional[User] = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    SessionCRUD.delete_all_user_auth_session(current_user, db)
    response.delete_cookie("session_id")

    return RedirectResponse("/", status_code=303)


@user_router.get("/{pk}")
@auth_only
async def get_user(
        request: Request,
        pk: UUID,
        page: int = Query(1, gt=0),
        limit: int = Query(10, gt=0),
        done_status: Optional[str] = Query(None),
        priority_id: Optional[int] = Query(None),
        text_search: Optional[str] = Query(None),
        sort_by_newest: Optional[bool] = Query(None),
        sort_by_oldest: Optional[bool] = Query(None),
        sort_by_ending: Optional[bool] = Query(None),
        db: Session = Depends(get_db),
        current_user: Optional[User] = Depends(get_current_user),
):
    if not current_user.is_staff and pk != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to access this page")

    if done_status is not None:
        done_status = done_status.lower()
        if done_status not in ['done', 'todo']:
            done_status = None

    user = UserCRUD.get_user_by_id(pk, db)
    request_tasks_result = RequestTaskCRUD.get_request_tasks(
        db,
        page,
        limit,
        done_status,
        priority_id,
        text_search,
        sort_by_newest,
        sort_by_oldest,
        sort_by_ending,
        creator_id=pk,
    )

    return templates.TemplateResponse(
        "user/user.html",
        {
            "request": request,
            "user": user,
            "current_user": current_user,
            "request_tasks": {"pagination": request_tasks_result},
            "filter": {
                "done_status": done_status if done_status is None else done_status.lower(),
            },
        },
    )
