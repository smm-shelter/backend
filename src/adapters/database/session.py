from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.settings import settings
print(settings.postgres_url)
engine = create_async_engine(settings.postgres_url)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
