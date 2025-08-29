from sqlalchemy.orm import Mapped

from .base import Base


class PetType(Base):
    __tablename__ = "petType"

    name: Mapped[str]

    def __str__(self):
        return f"{self.name}"
