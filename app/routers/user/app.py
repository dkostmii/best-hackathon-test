from typing import Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, Form, Query, HTTPException, Response, Request
from pydantic import ValidationError
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse

from app.dependencies import (
    auth_only,
    get_current_user,
    get_db,
    get_done_status,
    get_sort_by,
    handle_400_errors,
    templates,
)
from app.routers.user.crud import UserCRUD, SessionCRUD
from app.routers.user.model import User
from app.routers.user.schema import UserRegistrationSchema, UserLoginSchema
from app.routers.request_task.crud import RequestTaskCRUD, PrioritiesCRUD

user_router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@user_router.get("/register")
async def create_user_page(
        request: Request,
        is_staff: bool = Query(False),
        current_user: Optional[User] = Depends(get_current_user)
):
    """
    Render a webpage with a registration form for creating a new user.
    """

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
    """
    Create a new user based on registration form data.
    """

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
    """
    Render a webpage with a login form.
    """

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
    """
    Authenticate user login based on provided credentials.
    """

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
    """
    Perform user logout action, deleting authentication session.
    """

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
        sort_by: Optional[str] = Query(None),
        db: Session = Depends(get_db),
        current_user: Optional[User] = Depends(get_current_user),
):
    """
    Retrieve details of a specific user including associated request tasks.
    """

    if not current_user.is_staff and pk != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to access this page")

    done_status = get_done_status(done_status)

    sort_by = get_sort_by(sort_by)

    user = UserCRUD.get_user_by_id(pk, db)
    request_tasks_result = RequestTaskCRUD.get_request_tasks(
        db,
        page,
        limit,
        done_status,
        priority_id,
        text_search,
        sort_by,
        creator_id=pk,
    )

    priorities = PrioritiesCRUD.get_priorities(db)

    return templates.TemplateResponse(
        "user/user.html",
        {
            "request": request,
            "user": user,
            "current_user": current_user,
            "request_tasks": {"pagination": request_tasks_result},
            "filter": {
                "done_status": done_status if done_status is None else done_status.lower(),
                "text_search": text_search,
            },
            "sort": {
                "priority_id": priority_id,
                "sort_by": sort_by,
            },
            "priorities": priorities,
            "current_datetime": datetime.now(),
        },
    )
