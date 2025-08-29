from datetime import datetime

from sqlalchemy import TIMESTAMP, ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.utils.time import utc_signed_now

from .base import Base, BaseContent


class Article(Base):
    __tablename__ = "article"

    title: Mapped[str] = mapped_column(String(50))
    text: Mapped[str]

    pet_id: Mapped[int] = mapped_column(ForeignKey("pet.id"))

    publish_date: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=utc_signed_now
    )

    contents: Mapped[list["ArticleContent"]] = relationship(
        back_populates="article", lazy="selectin", cascade="all, delete-orphan"
    )

    images: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)

    def __str__(self):
        return f"{self.title}"


class ArticleContent(BaseContent):
    __tablename__ = "articleContents"
    article_id: Mapped[int] = mapped_column(ForeignKey("article.id"))
    article = relationship("Article", back_populates="contents", lazy="selectin")
