from pydantic import BaseModel


class PetStatusCreate(BaseModel):
    name: str


class PetStatusUpdate(BaseModel):
    name: str | None = None


class PetStatusGet(BaseModel):
    id: int
    name: str


class PetStatusList(BaseModel):
    id: int
    name: str
