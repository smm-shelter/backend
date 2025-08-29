from datetime import datetime

from sqlalchemy import ARRAY, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, BaseContent
from .enums import GenderEnum


class Pet(Base):
    __tablename__ = "pet"

    status_id: Mapped[str] = mapped_column(ForeignKey("petStatus.id"))
    status = relationship("PetStatus", lazy="selectin")
    
    type_id: Mapped[str] = mapped_column(ForeignKey("petType.id"))
    type = relationship("PetType", lazy="selectin")

    name: Mapped[str]

    gender: Mapped[GenderEnum] = mapped_column(default=GenderEnum.unknown)
    sterilized: Mapped[bool] = mapped_column(default=False)

    description: Mapped[str] = mapped_column(Text, nullable=True)

    year_birth: Mapped[int] = mapped_column(nullable=True)
    in_shelter_from: Mapped[datetime] = mapped_column(nullable=True)

    contents: Mapped[list["PetContent"]] = relationship(
        back_populates="pet", lazy="selectin", cascade="all, delete-orphan"
    )

    images: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)

    articles = relationship("Article", lazy="selectin", cascade="all, delete-orphan")

    def __str__(self):
        return f"{self.name}"


class PetContent(BaseContent):
    __tablename__ = "petContent"
    pet_id: Mapped[int] = mapped_column(ForeignKey("pet.id"))
    pet = relationship("Pet", back_populates="contents", lazy="selectin")
