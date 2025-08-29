from src.unit_of_work import UnitOfWork


class PetService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
    
    async def get_pets(
        self,
        type_of_pet: int | None,
        page: int,
        limit: int
    ):
        return await self.uow.repositories.pet.find_filtered_and_paginated(
            page=page,
            limit=limit,
            **(dict(type_id=type_of_pet) if type_of_pet is not None else dict())
        )
    
    async def get_one_pet(self, id: int):
        return await self.uow.repositories.pet.find_one(
            id=id
        )

