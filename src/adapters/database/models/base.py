from datetime import datetime

from sqlalchemy import BIGINT, TIMESTAMP, String
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.utils.time import utc_signed_now


class Base(AsyncAttrs, DeclarativeBase):
    """
    Base class that provides metadata and id with int4
    """

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)


class BaseWithTelemetryTimestamps(Base):
    __abstract__ = True
    create_date: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=utc_signed_now
    )
    modify_date: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=utc_signed_now, onupdate=utc_signed_now
    )


class BaseContent(BaseWithTelemetryTimestamps):
    __abstract__ = True
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(50), default="a")
    uri: Mapped[str]
    comment: Mapped[str] = mapped_column(String(255), nullable=True)
