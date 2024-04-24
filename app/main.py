from fastapi import FastAPI, HTTPException, Request

from app.routers import app_router, templates

base_app = FastAPI()
base_app.include_router(app_router)


@base_app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: Exception):
    return templates.TemplateResponse(
        name="error.html",
        context={
            "request": request,
            "error": {"title": "Error occurred", "description": exc.detail},
            "no_auth_controls": True,
        }
    )
