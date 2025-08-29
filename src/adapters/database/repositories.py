from src.utils.repository import SQLAlchemyRepository, SQLALchemyUserRepository

from .models import (
    Article,
    ArticleContent,
    Manager,
    News,
    NewsContent,
    Pet,
    PetContent,
    PetStatus,
    PetType,
    Transaction,
    TransactionContent,
)


class ArticleRepository(SQLAlchemyRepository):
    model = Article


class ArticleContentRepository(SQLAlchemyRepository):
    model = ArticleContent


class ManagerRepository(SQLALchemyUserRepository):
    model = Manager


class NewsRepository(SQLAlchemyRepository):
    model = News


class NewsContentRepository(SQLAlchemyRepository):
    model = NewsContent


class PetRepository(SQLAlchemyRepository):
    model = Pet


class PetContentRepository(SQLAlchemyRepository):
    model = PetContent


class PetTypeRepository(SQLAlchemyRepository):
    model = PetType


class PetStatusRepository(SQLAlchemyRepository):
    model = PetStatus


class TransactionRepository(SQLAlchemyRepository):
    model = Transaction


class TransactionContentRepository(SQLAlchemyRepository):
    model = TransactionContent
