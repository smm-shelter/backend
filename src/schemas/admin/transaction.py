from datetime import datetime

from pydantic import BaseModel, Field
from src.utils.time import utc_signed_now

class TransactionCreate(BaseModel):
    incoming: bool = False
    date_of_payment: datetime = Field(default_factory=utc_signed_now)
    amount: int
    sender_receiver: str | None = None
    comment: str | None = None


class TransactionUpdate(BaseModel):
    incoming: bool | None = None
    date_of_payment: datetime | None = None
    amount: int | None = None
    sender_receiver: str | None = None
    comment: str | None = None


class TransactionGet(BaseModel):
    id: int
    incoming: bool
    date_of_payment: datetime | None = None
    amount: int
    sender_receiver: str | None = None
    comment: str | None = None


class TransactionList(BaseModel):
    id: int
    incoming: bool
    amount: int
    sender_receiver: str | None = None
    comment: str | None = None
