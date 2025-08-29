from datetime import datetime

from sqlalchemy import TIMESTAMP, ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.utils.time import utc_signed_now

from .base import Base, BaseContent


class News(Base):
    __tablename__ = "news"

    title: Mapped[str] = mapped_column(String(50))
    text: Mapped[str]

    publish_date: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=utc_signed_now
    )

    contents: Mapped[list["NewsContent"]] = relationship(
        back_populates="news", lazy="selectin", cascade="all, delete-orphan"
    )

    images: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)

    def __str__(self):
        return f"{self.title}"


class NewsContent(BaseContent):
    __tablename__ = "newsContents"
    news_id: Mapped[int] = mapped_column(ForeignKey("news.id"))
    news = relationship("News", back_populates="contents", lazy="selectin")
