from pydantic import BaseModel

from src.adapters.database.models import GenderEnum

class PetCreate(BaseModel):
    status_id: int
    name: str
    gender: GenderEnum
    description: str | None = None
    sterilized: bool = False
    type_id: int


class PetUpdate(BaseModel):
    status_id: int | None = None
    name: str | None = None
    gender: GenderEnum | None = None
    description: str | None = None
    sterilized: bool | None = None
    type_id: int | None = None


class PetGet(BaseModel):
    id: int
    status_id: int
    name: str
    gender: GenderEnum
    description: str | None = None
    sterilized: bool
    type_id: int


class PetList(BaseModel):
    id: int
    name: str
    gender: GenderEnum
    sterilized: bool
