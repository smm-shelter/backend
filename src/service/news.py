from src.unit_of_work import UnitOfWork

from src.adapters.database.models import News

class NewsService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
    
    async def get_news(
        self,
        page: int,
        limit: int
    ):
        return await self.uow.repositories.news.find_filtered_and_paginated(
            page=page,
            limit=limit,
        )
    
    async def get_one_news(self, id: int):
        return await self.uow.repositories.news.find_one(id=id)

