from pydantic import BaseModel


class PetTypeCreate(BaseModel):
    name: str


class PetTypeUpdate(BaseModel):
    name: str | None = None


class PetTypeGet(BaseModel):
    id: int
    name: str


class PetTypeList(BaseModel):
    id: int
    name: str
