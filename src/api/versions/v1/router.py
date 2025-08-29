from fastapi import APIRouter

from .pet import pet_router
from .news import news_router

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(pet_router)
v1_router.include_router(news_router)
