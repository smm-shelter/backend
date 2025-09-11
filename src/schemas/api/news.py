from datetime import datetime

from pydantic import BaseModel, ConfigDict
from .content import ContentSchema


class NewsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    text: str
    publish_date: datetime

    contents: list[ContentSchema]
