from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NewsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    text: str
    publish_date: datetime
