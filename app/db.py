from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


engine = create_async_engine(settings.database_url_asyncpg, echo=False, future=True)

SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


class Base(DeclarativeBase):
    pass


@asynccontextmanager
async def transaction_session():
    async with SessionLocal() as session:
        async with session.begin():
            yield session


async def get_db() -> AsyncSession:  # type: ignore
    async with transaction_session() as session:
        yield session  # type: ignore
