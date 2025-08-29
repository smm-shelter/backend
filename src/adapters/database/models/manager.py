from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Manager(Base):
    __tablename__ = "manager"

    first_name: Mapped[str] = mapped_column(String(50))
    second_name: Mapped[str] = mapped_column(String(50))

    phone: Mapped[str] = mapped_column(String(11), unique=True)
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    password: Mapped[str] = mapped_column(String(60))

    def __str__(self):
        return f"{self.first_name} {self.second_name}"
