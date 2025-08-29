from datetime import datetime

from pydantic import BaseModel, Field


class NewsCreate(BaseModel):
    title: str = Field(..., max_length=50)
    text: str


class NewsUpdate(BaseModel):
    title: str | None = Field(None, max_length=50)
    text: str | None = None


class NewsGet(BaseModel):
    id: int
    title: str
    text: str
    publish_date: datetime


class NewsList(BaseModel):
    id: int
    title: str
    text: str
