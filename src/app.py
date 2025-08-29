from fastadmin import fastapi_app as admin_app
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from src.api import main_api_router

from src.settings import settings
from src.utils.exceptions import (
    ResultNotFound,
)

app = FastAPI(
    title="zooprim backend",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(settings.ADMIN_PATH, admin_app, "admin panel")

app.include_router(main_api_router)


@app.exception_handler(ResultNotFound)
async def not_found_exception_handler(request: Request, exc: ResultNotFound):
    return JSONResponse(
        status_code=404,
        content={"detail": "Result not found"},
    )

