from sqlalchemy.ext.asyncio import AsyncSession

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

from .repository import SQLAlchemyRepository, SQLALchemyUserRepository


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



class RepositoriesGateway:
    def __init__(self, session: AsyncSession):
        self.article = ArticleRepository(session)
        self.article_content = ArticleContentRepository(session)
        self.manager = ManagerRepository(session)
        self.news = NewsRepository(session)
        self.news_content = NewsContentRepository(session)
        self.pet = PetRepository(session)
        self.pet_content = PetContentRepository(session)
        self.pet_type = PetTypeRepository(session)
        self.pet_status = PetStatusRepository(session)
        self.transaction = TransactionRepository(session)
        self.transaction_content = TransactionContentRepository(session)
