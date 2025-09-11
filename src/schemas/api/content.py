from pydantic import BaseModel, ConfigDict

class ContentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uri: str
