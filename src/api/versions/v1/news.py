from typing import Annotated
from fastapi import APIRouter, Query, Path, Depends

from src.unit_of_work import UnitOfWork
from src.service import NewsService
from src.schemas.api import NewsSchema

news_router = APIRouter(prefix="/news", tags=["News"])

@news_router.get(
    "/list",
    response_model=list[NewsSchema],
)
async def get_news(
    uow: Annotated[UnitOfWork, Depends(UnitOfWork)],
    page: Annotated[int, Query()] = 1,
    limit: Annotated[int, Query()] = 20,
):
    async with uow:
        result = await NewsService(uow).get_news(
            page=page,
            limit=limit,
        )
        return [
            NewsSchema.model_validate(result_i)
            for result_i in result
        ]


@news_router.get(
    "/one/{id}",
    response_model=NewsSchema,
)
async def get_one_news(
    uow: Annotated[UnitOfWork, Depends(UnitOfWork)],
    id: Annotated[int, Path()],
):
    async with uow:
        record = await NewsService(uow).get_one_news(id=id)
        return NewsSchema.model_validate(record)
