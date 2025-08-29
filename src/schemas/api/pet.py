from pydantic import BaseModel, ConfigDict

from src.adapters.database.models import GenderEnum

class PetSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status_id: int
    name: str
    gender: GenderEnum
    description: str | None = None
    sterilized: bool
    type_id: int

