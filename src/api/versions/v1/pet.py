from typing import Annotated
from fastapi import APIRouter, Query, Path, Depends

from src.unit_of_work import UnitOfWork
from src.service import PetService
from src.schemas.api import PetSchema

pet_router = APIRouter(prefix="/pet", tags=["Pets"])

@pet_router.get(
    "/list",
    response_model=list[PetSchema]
)
async def get_pets(
    uow: Annotated[UnitOfWork, Depends(UnitOfWork)],
    type_of_pet: Annotated[int | None, Query()] = None,
    page: Annotated[int, Query()] = 1,
    limit: Annotated[int, Query()] = 20,
):
    async with uow:
        result = await PetService(uow).get_pets(
            type_of_pet=type_of_pet,
            page=page,
            limit=limit,
        )

        return [
            PetSchema.model_validate(result_i)
            for result_i in result
        ]


@pet_router.get(
    "/one/{id}",
    response_model=PetSchema,
)
async def get_one_pet(
    uow: Annotated[UnitOfWork, Depends(UnitOfWork)],
    id: Annotated[int, Path()],
):
    async with uow:
        record = await PetService(uow).get_one_pet(
            id=id
        )
        return PetSchema.model_validate(record)
