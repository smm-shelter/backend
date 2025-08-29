from sqlalchemy.orm import Mapped

from .base import Base


class PetStatus(Base):
    __tablename__ = "petStatus"

    name: Mapped[str]

    def __str__(self):
        return f"{self.name}"
