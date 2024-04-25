from fastapi import FastAPI, HTTPException, Request

from app.routers import app_router, templates


base_app = FastAPI()
base_app.include_router(app_router)


@base_app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        name="error.html",
        context={
            "request": request,
            "error": {"title": "Not found", "description": exc.detail, "status": exc.status_code},
            "no_auth_controls": True,
        }
    )


@base_app.exception_handler(HTTPException)
async def server_error_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        name="error.html",
        context={
            "request": request,
            "error": {"title": "Server error occurred", "description": exc.detail, "status": exc.status_code},
            "no_auth_controls": True,
        }
    )
