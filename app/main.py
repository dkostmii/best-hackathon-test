from fastapi import FastAPI, HTTPException, Request

from app.routers import app_router, templates


base_app = FastAPI(
    title="Help Request Portal",
    description="This Portal facilitates the process of providing assistance to people in need, making it easier to "
                "connect those who provide help.",
    version="1.0.0",
)
base_app.include_router(app_router)


@base_app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        name="error.html",
        context={
            "request": request,
            "error": {"title": "Not found", "description": exc.detail, "status": exc.status_code},
            "no_auth_controls": True,
        },
        status_code=exc.status_code,
    )


@base_app.exception_handler(HTTPException)
async def server_error_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        name="error.html",
        context={
            "request": request,
            "error": {"title": "Server error occurred", "description": exc.detail, "status": exc.status_code},
            "no_auth_controls": True,
        },
        status_code=exc.status_code,
    )
